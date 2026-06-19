# 🚁 Drone UI Intelligence System

Real-time object detection, size estimation, distance measurement, and HUD overlay for drone camera feeds — built with YOLOv8 and OpenCV.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 Object Detection | YOLOv8n — real-time inference on video or webcam |
| 📏 Size Estimation | Physics-based pinhole camera model, per-class real dimensions |
| 📡 Distance Estimation | Pinhole formula using known object heights |
| 🖱️ Mouse Measuring Tool | Click & drag to measure real-world distance on screen |
| 🎨 HUD Overlay | Semi-transparent panels, corner brackets, threat colour coding |
| 🔴🟡🟢 Threat Levels | CLOSE / APPROACHING / SAFE classification |
| 🚗 Movement Tracking | Centroid-based frame-to-frame tracking |
| 💾 Output Saving | Save processed video with overlays |

---

## 🐛 Scale Factor Fix (Key Improvement)

The original code used a flat multiplier (`pixel_width × 0.002`) for size estimation — this only worked for persons and badly misestimated all other classes (a car showed `1.76 m` instead of `~4.5 m`).

**Fix**: Replaced with the **pinhole camera model** with per-class known dimensions:

```
distance = (real_height × focal_length) / pixel_height
real_width = (pixel_width / focal_length) × distance
```

Each YOLO class (car, truck, bus, person, etc.) now uses its correct real-world dimensions.

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install ultralytics opencv-python numpy
```

### 2. Run on webcam

```bash
python backend/main.py
```

### 3. Run on a video file

```bash
python backend/main.py --source "data/your_video.mp4"
```

### 4. Run and save output

```bash
python backend/main.py --source "data/your_video.mp4" --output "data/output.mp4"
```

---

## 🎮 Controls

| Key / Action | Effect |
|---|---|
| `C` | Calibrate focal length using current detected object |
| `SPACE` | Pause / Resume |
| `ESC` | Exit |
| **Left-click & drag** | Draw measurement ruler between two points |
| **Right-click** | Clear the ruler |

---

## 📁 Project Structure

```
drone-ui-intelligence-system/
├── backend/
│   ├── main.py          # Main pipeline (capture → detect → estimate → display)
│   ├── detector.py      # YOLOv8 inference wrapper
│   ├── estimator.py     # Physics-based size & distance estimation
│   ├── utils.py         # HUD / overlay rendering
│   └── config.py        # Camera params, object dimensions, confidence thresholds
├── data/
│   └── README.md        # Data folder instructions (videos not committed)
├── docs/
│   └── architecture.md  # System architecture documentation
├── models/
│   └── yolov8n.pt       # YOLOv8 nano weights (auto-downloaded)
└── requirements.txt
```

---

## 📐 Architecture

```
Camera / Video  →  YOLOv8 Detection  →  Estimation Engine  →  HUD Overlay
                         ↓                      ↓
                   Confidence Filter      Pinhole Camera Model
                   (per-class min)        (per-class dimensions)
```

---

## ⚙️ Configuration (`backend/config.py`)

| Parameter | Description |
|---|---|
| `FOCAL_LENGTH_PX` | Camera focal length in pixels |
| `ALTITUDE` | Drone altitude in metres (used for ruler tool) |
| `KNOWN_DIMENSIONS` | Per-class real height & width (metres) |
| `GLOBAL_MIN_CONFIDENCE` | Minimum detection confidence (default 0.40) |
| `MIN_CONFIDENCE_PER_CLASS` | Per-class overrides (e.g. `train: 0.82` to suppress false positives) |

---

## 🔮 Future Work

- MAVLink / DJI SDK integration for live telemetry altitude
- GPU-accelerated inference
- Persistent object IDs (DeepSORT / ByteTrack)
- Flutter-based mobile UI
- Multi-camera support
