import cv2
import sys

print('========================================')
print('VisionGuard: Laptop Webcam Diagnostic')
print('========================================')

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('[ERROR] Unable to open webcam at index 0.')
    print('Please check if camera permissions are granted or another app is using the webcam.')
    sys.exit(1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

print(f'[SUCCESS] Webcam opened successfully!')
print(f'Resolution: {width}x{height} | FPS: {fps}')

ret, frame = cap.read()
if ret and frame is not None:
    print(f'[SUCCESS] Captured test frame of shape {frame.shape}. Webcam is functioning properly.')
else:
    print('[WARNING] Camera opened but failed to retrieve frame.')

cap.release()
print('Diagnostic complete.')
