# 🏗️ System Architecture – Drone UI Intelligence System

## 📌 Overview

This system is designed to provide **real-time situational awareness** using a drone camera feed.  
It combines **computer vision + telemetry + UI overlay** to assist decision-making.

---

## 🧠 High-Level Architecture


Camera Feed → Object Detection → Estimation Engine → Intelligence Layer → UI Overlay


---

## 🔁 Data Flow Pipeline

### 1. 🎥 Input Layer (Camera Feed)
- Source: Webcam (MVP) / Drone camera (future)
- Captured using OpenCV
- Provides real-time video frames

---

### 2. 🧠 Object Detection Layer
- Model: YOLOv8 (Ultralytics)
- Detects objects in each frame
- Outputs:
  - Bounding boxes
  - Class labels (person, car, etc.)
  - Confidence scores

---

### 3. 📏 Estimation Engine

#### 🔹 Size Estimation
- Uses pixel width of object
- Applies calibration factor:
  

Real Size = Pixel Width × Scale


- Scale derived using a known reference object

---

#### 🔹 Distance Estimation
- Based on pinhole camera model:


Distance = (Real Height × Focal Length) / Pixel Height


- Requires:
- Known object height
- Calibrated focal length

---

### 4. 🧠 Intelligence Layer

Adds contextual meaning to raw detections:

- Movement detection (frame-to-frame comparison)
- Status classification:
- SAFE
- APPROACHING
- CLOSE
- Basic object tracking (centroid-based)

---

### 5. 🖥️ UI / HUD Layer

Rendered using OpenCV:

- Bounding boxes
- HUD panel (label + size + distance)
- Color-coded threat levels:
- 🔴 Close
- 🟡 Medium
- 🟢 Safe
- Crosshair (center targeting)

---

## ⚙️ Components Breakdown

| Component        | File              | Responsibility |
|-----------------|------------------|----------------|
| Main Pipeline    | main.py          | Orchestrates system |
| Detector         | detector.py      | YOLO inference |
| Estimator        | estimator.py     | Size & distance |
| UI Renderer      | utils.py         | Overlay drawing |
| Config           | config.py        | Constants |

---

## 🔄 Current vs Future Architecture

### ✅ Current (MVP)
- Webcam input
- Simulated telemetry
- Local processing

### 🚀 Future Enhancements
- Drone telemetry (MAVLink / DJI SDK)
- Flutter-based UI
- Cloud processing (optional)
- Multi-object tracking
- Target prioritization

---

## ⚠️ Limitations

- Approximate size & distance (depends on calibration)
- Single-camera depth estimation
- Basic tracking (no persistent IDs yet)

---

## 🎯 Key Innovation

- Fusion of:
- Computer vision (YOLO)
- Telemetry-based estimation
- Actionable UI overlay

👉 Transforms raw detection into **decision-support system**

---

## 📌 Conclusion

This architecture provides a scalable foundation for:
- Tactical drone interfaces
- Surveillance systems
- Real-time analytics platforms

Future upgrades will focus on improving:
- Accuracy
- UI sophistication
- Drone integration