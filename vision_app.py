import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
import threading

print('=' * 60)
print('  VisionGuard: Live Driver Fatigue & Distraction Monitor')
print('  Press [Q] in the camera window to exit.')
print('=' * 60)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Key landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH = [61, 291, 13, 14]

# 3D points for head pose
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose tip
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),  # Left eye corner
    (225.0, 170.0, -135.0),   # Right eye corner
    (-150.0, -150.0, -125.0), # Left mouth corner
    (150.0, -150.0, -125.0)   # Right mouth corner
], dtype=np.float64)

POSE_INDICES = [1, 152, 33, 263, 61, 291]

def euclidean_dist(p1, p2):
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))

def calculate_ear(landmarks, eye_indices, w, h):
    pts = [(landmarks[idx].x * w, landmarks[idx].y * h) for idx in eye_indices]
    p1, p2, p3, p4, p5, p6 = pts
    v1 = euclidean_dist(p2, p6)
    v2 = euclidean_dist(p3, p5)
    horiz = euclidean_dist(p1, p4)
    if horiz == 0:
        return 0.0
    return (v1 + v2) / (2.0 * horiz)

def calculate_mar(landmarks, mouth_indices, w, h):
    pts = [(landmarks[idx].x * w, landmarks[idx].y * h) for idx in mouth_indices]
    p_left, p_right, p_top, p_bot = pts
    vert = euclidean_dist(p_top, p_bot)
    horiz = euclidean_dist(p_left, p_right)
    if horiz == 0:
        return 0.0
    return vert / (2.0 * horiz)

def estimate_head_pose(landmarks, w, h):
    img_pts = np.array([(landmarks[idx].x * w, landmarks[idx].y * h) for idx in POSE_INDICES], dtype=np.float64)
    focal = w
    center = (w / 2, h / 2)
    cam_mat = np.array([[focal, 0, center[0]], [0, focal, center[1]], [0, 0, 1]], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1))
    success, rvec, tvec = cv2.solvePnP(MODEL_POINTS, img_pts, cam_mat, dist_coeffs)
    if not success:
        return 0.0, 0.0
    rmat, _ = cv2.Rodrigues(rvec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    return float(angles[0]), float(angles[1]) # pitch, yaw

# Alarm sound thread
alarm_playing = False
def play_beep():
    global alarm_playing
    if not alarm_playing:
        alarm_playing = True
        try:
            winsound.Beep(1200, 300)
        except Exception:
            pass
        alarm_playing = False

# Open Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('[ERROR] Could not open webcam at index 0!')
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

drowsy_counter = 0
DROWSY_THRESHOLD_FRAMES = 30 # approx 1.5s at ~20-25 fps
EAR_THRESHOLD = 0.21
MAR_THRESHOLD = 0.65

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        curr_time = time.time()
        fps = 1.0 / max(0.001, (curr_time - prev_time))
        prev_time = curr_time

        # Semi-transparent HUD header bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (20, 20, 20), -1)
        cv2.rectangle(overlay, (0, h - 60), (w, h), (20, 20, 20), -1)
        frame = cv2.addWeighted(overlay, 0.65, frame, 0.35, 0)

        if results.multi_face_landmarks:
            mesh = results.multi_face_landmarks[0].landmark

            # Calculate metrics
            left_ear = calculate_ear(mesh, LEFT_EYE, w, h)
            right_ear = calculate_ear(mesh, RIGHT_EYE, w, h)
            ear = (left_ear + right_ear) / 2.0
            mar = calculate_mar(mesh, MOUTH, w, h)
            pitch, yaw = estimate_head_pose(mesh, w, h)

            # Draw green landmark dots on eyes and lips
            for idx in LEFT_EYE + RIGHT_EYE:
                cx, cy = int(mesh[idx].x * w), int(mesh[idx].y * h)
                cv2.circle(frame, (cx, cy), 2, (0, 255, 255), -1)

            for idx in MOUTH:
                cx, cy = int(mesh[idx].x * w), int(mesh[idx].y * h)
                cv2.circle(frame, (cx, cy), 2, (255, 0, 255), -1)

            # Drowsiness detection logic
            if ear < EAR_THRESHOLD:
                drowsy_counter += 1
            else:
                drowsy_counter = max(0, drowsy_counter - 2)

            is_drowsy = (drowsy_counter >= DROWSY_THRESHOLD_FRAMES)
            is_distracted = (pitch < -20.0 or abs(yaw) > 30.0)
            is_yawning = (mar > MAR_THRESHOLD)

            # Header info
            cv2.putText(frame, f'FPS: {int(fps)}', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
            cv2.putText(frame, f'EAR: {ear:.2f}', (150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if ear >= EAR_THRESHOLD else (0, 0, 255), 2)
            cv2.putText(frame, f'MAR: {mar:.2f}', (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            cv2.putText(frame, f'Pitch: {pitch:.0f} deg', (450, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

            # Warning Status Banner
            if is_drowsy:
                # Flashing Red Alert Box
                cv2.rectangle(frame, (30, 100), (w - 30, 210), (0, 0, 255), -1)
                cv2.rectangle(frame, (25, 95), (w - 25, 215), (255, 255, 255), 3)
                cv2.putText(frame, 'CRITICAL WARNING: DROWSINESS DETECTED!', (50, 150), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
                cv2.putText(frame, 'PLEASE WAKE UP & FOCUS ON THE ROAD!', (70, 190), cv2.FONT_HERSHEY_DUPLEX, 0.7, (200, 255, 255), 2)
                threading.Thread(target=play_beep, daemon=True).start()
                status_text = 'STATE: CRITICAL (DROWSY)'
                status_color = (0, 0, 255)
            elif is_distracted:
                # Orange Warning
                cv2.rectangle(frame, (50, 100), (w - 50, 180), (0, 140, 255), -1)
                cv2.rectangle(frame, (45, 95), (w - 45, 185), (255, 255, 255), 2)
                cv2.putText(frame, 'WARNING: DRIVER DISTRACTED (HEAD TILT / PHONE)!', (70, 150), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)
                status_text = 'STATE: DISTRACTED'
                status_color = (0, 140, 255)
            elif is_yawning:
                # Yellow Warning
                cv2.rectangle(frame, (60, 100), (w - 60, 180), (0, 215, 255), -1)
                cv2.putText(frame, 'WARNING: FREQUENT YAWNING DETECTED', (90, 150), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
                status_text = 'STATE: YAWNING'
                status_color = (0, 215, 255)
            elif ear < EAR_THRESHOLD:
                # Blinking / Eyes closing early warning
                status_text = f'STATE: EYES CLOSING ({drowsy_counter}/{DROWSY_THRESHOLD_FRAMES})'
                status_color = (0, 165, 255)
            else:
                status_text = 'STATE: ATTENTIVE (SAFE)'
                status_color = (0, 255, 0)

            # Footer status
            cv2.putText(frame, status_text, (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            cv2.putText(frame, 'VisionGuard Driver Monitor [Press Q to exit]', (w - 380, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        else:
            # No face detected
            drowsy_counter = 0
            cv2.putText(frame, 'NO DRIVER DETECTED IN CAMERA FRAME', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            cv2.putText(frame, 'STATE: NO FACE', (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow('VisionGuard: Live Driver Safety HUD', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print('[INFO] VisionGuard monitor closed cleanly.')
