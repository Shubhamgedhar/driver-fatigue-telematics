# 🚗 VisionGuard: Edge-Vision Driver Fatigue & Distraction Detection System

> **A Real-Time In-Cabin Driver Safety & Fleet Telematics Platform**  
> *Developed for 3rd Year Computer Science Lab / Capstone Evaluation*

[![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](https://www.java.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-007ACC?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)](https://spring.io/projects/spring-boot)
[![PostgreSQL/SQLite](https://img.shields.io/badge/SQL_Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

---

## 📌 1. Project Overview & Motivation

Driver drowsiness, microsleeps, and mobile phone distractions cause over **20% of fatal vehicle collisions worldwide**. Commercial truck operators, municipal transit drivers, and ride-share contractors regularly endure prolonged hours behind the wheel, where cognitive exhaustion can impair reaction times within fractions of a second.

Conventional vehicle telematics (such as harsh braking or lane drift monitoring) are **purely reactive**—they flag hazards only *after* vehicle stability has already been compromised. 

**VisionGuard** is a proactive, non-invasive in-cabin monitoring platform that runs **100% in software** using standard laptop webcams or dashcam video streams. By analyzing real-time facial landmark topology, the system detects micro-behaviors (eye aspect ratios, blink durations, yawning, and head tilts), triggers immediate in-cabin audio alarms, and streams hazard telemetry to an enterprise fleet control room.

---

## 🔬 2. The Core Scientific Algorithms

The system tracks **468 3D facial landmarks** in real time to calculate three biometric indicators:

`
      P2     P3                          P2     P3
       ●─────●                            ●─────●
   P1 ●       ● P4                  P1 ●           ● P4
       ●─────●                            ●─────●
      P6     P5                          P6     P5
   [ Open Eye: High EAR ]             [ Closed Eye: Low EAR ≈ 0 ]
`

### A. Eye Aspect Ratio (EAR) — *Detects Drowsiness & Microsleeps*
Uses 6 landmark coordinates per eye to measure vertical opening relative to horizontal width:
\text{EAR} = \frac{\|P_2 - P_6\| + \|P_3 - P_5\|}{2 \cdot \|P_1 - P_4\|}

* **Normal Awake State**: $\text{EAR} \approx 0.28 - 0.35$
* **Blinking State**: $\text{EAR} < 0.20$ (lasts $< 0.3$ seconds)
* **Microsleep / Drowsiness Alarm**: If $\text{EAR} < 0.20$ continuously for **$\ge 2.0$ seconds** (40–60 consecutive frames), an immediate critical audio alarm is sounded.

### B. Mouth Aspect Ratio (MAR) — *Detects Yawning*
Measures lip vertical distance over horizontal width:
\text{MAR} = \frac{\|M_2 - M_4\|}{2 \cdot \|M_1 - M_3\|}
* If $\text{MAR} > 0.65$ for $\ge 3.0$ seconds $\rightarrow$ **Yawning Warning** logged.

### C. Head Pose Euler Angles (Pitch, Yaw, Roll) — *Detects Distraction*
* **Pitch Down $> 25^\circ$**: Driver looking down (e.g., texting on mobile phone).
* **Yaw Left/Right $> 35^\circ$**: Driver looking away from the road for prolonged periods.

---

## 🏗️ 3. System Architecture & Tech Stack

`
[ Laptop Webcam / Video Stream ]
               │
               ▼
[ Python 3.11 Edge-Vision Engine (OpenCV + Google MediaPipe) ]
  • Captures frames at 30-60 FPS
  • Extracts 468 3D facial landmark coordinates
               │
               ▼ (Memory buffer via JNI)
[ C++ Native JNI Module (FastGeometry.dll / .so) ]
  • SIMD-accelerated Euclidean distance vector math
  • Computes EAR, MAR, and Head Pose in < 0.5 ms
               │
               ▼ (JSON over WebSockets / HTTP)
[ Java Spring Boot Core Controller (JVM Backend) ]  <── CORE JAVA ENGINE
  • Sliding-window consecutive frame state machine
  • Triggers audible warning siren via Java Sound API / Web Audio
  • Multi-threaded telemetry ingestion pool
  • Embedded SQLite / PostgreSQL persistence for audit logs
               │
               ├───────────────────────────────┐
               ▼                               ▼
[ Relational SQL Database ]         [ Modern Web Cockpit HUD ]
  • Trips & driver records           • Live camera feed + glowing face mesh
  • Timestamped violation logs       • Real-time EAR / MAR visual dials
  • Fleet risk analytics             • Dynamic route map (Leaflet.js)
`

### Why Each Technology Was Chosen:
1. **Java (Spring Boot / Sockets)**: Central enterprise coordinator, thread safety, sliding-window state machines, REST APIs, and database persistence.
2. **C++ (via JNI)**: Low-level native vector math without Java garbage collection pauses, showcasing systems-level cross-language programming.
3. **Machine Learning / Python**: MediaPipe pre-trained face mesh topology providing accurate 30+ FPS landmarking on standard consumer CPUs without requiring a GPU.
4. **SQL (PostgreSQL / SQLite)**: Relational audit trail capturing every fatigue hazard event with timestamps, severity scores, and trip duration.
5. **HTML5 / CSS3 / JavaScript**: Modern automotive cockpit dashboard with Canvas rendering and WebSockets.

---

## 📂 4. Project Structure

`
driver-fatigue-telematics/
├── .gitignore
├── README.md
│
├── vision-engine/                        # [Python & MediaPipe Module]
│   ├── requirements.txt                  # opencv-python, mediapipe, websockets
│   ├── vision_detector.py                # Live webcam landmark extractor
│   └── test_cam.py                       # Camera diagnostic test tool
│
├── native-core/                          # [C++ Native Module via JNI]
│   ├── include/
│   │   └── FastGeometry.h                # JNI header definition
│   ├── src/
│   │   └── FastGeometry.cpp              # C++ Euclidean distance & EAR math
│   └── compile.bat                       # Script to compile FastGeometry.dll
│
├── backend-java/                         # [Core Java Enterprise Engine]
│   ├── pom.xml                           # Maven dependencies (Spring Boot, WebSocket, SQLite)
│   └── src/main/java/com/visionguard/
│       ├── VisionGuardApplication.java   # Spring Boot entry point
│       ├── model/                        # Trip, Driver, ViolationEvent entities
│       ├── service/                      # FatigueEngine, JNI Service, Sound Alert
│       └── controller/                   # WebSocket telemetry & REST endpoints
│
└── web-hud/                              # [Interactive In-Cabin Dashboard]
    ├── index.html                        # Driver cockpit HUD & fleet map
    ├── css/
    │   └── hud-style.css                 # Dark automotive UI theme
    └── js/
        ├── app.js                        # WebSocket client, sound sirens, state alerts
        └── visualizer.js                 # HTML5 Canvas real-time face mesh renderer
`

---

## 🚀 5. Quick Start & Demonstration Guide

### Prerequisites
* **Java**: OpenJDK 17 or higher
* **Python**: Python 3.10+ (opencv-python, mediapipe, websockets)
* **Browser**: Chrome, Edge, or Firefox (with webcam permissions enabled)

### Step 1: Install Python Dependencies
`ash
pip install opencv-python mediapipe websockets flask flask-cors
`

### Step 2: Test Laptop Camera
`ash
python vision-engine/test_cam.py
`

### Step 3: Run the Vision Engine & Java Backend
`ash
# Terminal 1: Run Python Vision Engine
python vision-engine/vision_detector.py

# Terminal 2: Run Java Backend
cd backend-java
mvn spring-boot:run
`

### Step 4: Open Web Dashboard
Open http://localhost:8080 (or web-hud/index.html) in your browser to start the live cockpit demo.

---

## 🎯 6. Live Evaluation & Demo Steps for Examiners

1. **Normal Driving**: Look directly at the laptop webcam. The dashboard displays Status: ATTENTIVE (100%) with a green EAR gauge $\approx 0.32$.
2. **Drowsiness / Microsleep Trigger**: Close your eyes for **2.5 seconds**. The screen flashes red, a loud audible siren sounds, and a MICROSLEEP VIOLATION is written to the database.
3. **Phone Distraction Trigger**: Look downward at your phone. The system immediately flags DISTRACTION: HEAD TILT DETECTED.
4. **Database Verification**: Open the violation log view to show timestamped incident records recorded live in the SQL database.

---

## 📊 7. Benchmark Datasets for Empirical Verification

* **State Farm Distracted Driver Detection (Kaggle)**: 100,000+ labeled images of drivers under various distraction scenarios.
* **NTHU Driver Drowsiness Detection Dataset (NTHU-DDD)**: Real video footage of drivers nodding off, blinking slowly, and yawning under varying lighting conditions.
* **YawDD (Yawning Detection Dataset)**: 300+ in-car video clips testing mouth aspect ratios and yawning frequencies.

---

## 👤 Author & Repository
* **Author**: Shubham Gedhar
* **GitHub**: [@Shubhamgedhar](https://github.com/Shubhamgedhar)
* **Repository**: [driver-fatigue-telematics](https://github.com/Shubhamgedhar/driver-fatigue-telematics)
