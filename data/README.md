# 📂 Data Folder

This folder contains drone video footage used for testing the Drone UI Intelligence System.

## ⚠️ Videos Not Included in Repo

Video files (`.mp4`, `.avi`, etc.) are excluded from version control because they exceed GitHub's 100 MB file size limit.

## 🎬 How to Use

Place your drone video file(s) in this folder and run:

```bash
# Run on a video file
python backend/main.py --source "data/your_video.mp4"

# Run and save processed output
python backend/main.py --source "data/your_video.mp4" --output "data/output.mp4"

# Run on live webcam
python backend/main.py --source 0
```

## 🎥 Test Video

The system was developed and tested on:

| File | Resolution | Duration | FPS |
|------|-----------|----------|-----|
| `Rec_0009.mp4` | 640×384 | ~22.5 min | 30 fps |

**Content**: Aerial drone footage of an urban area — cars, trucks, trains, buses, and pedestrians detected.

## 📁 Expected Structure

```
data/
├── README.md            ← this file
├── Rec_0009.mp4         ← test video (not committed, add manually)
└── Rec_0009_output.mp4  ← processed output (auto-generated, not committed)
```
