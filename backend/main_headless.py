import cv2
import os
from detector import ObjectDetector
from estimator import Estimator, ALTITUDE
from utils import draw_overlay, draw_altitude

# Create output directory
os.makedirs("output", exist_ok=True)

detector = ObjectDetector()
estimator = Estimator()

cap = cv2.VideoCapture("../data/Rec_0009.mp4")

prev_positions = {}
ALLOWED_CLASSES = ["person", "car", "truck", "bus"]

print("🚀 Running on drone video (headless mode)...")
print("📁 Saving frames to 'output' directory...")

frame_count = 0
detection_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print(f"🎬 Video ended - processed {frame_count} frames")
        break

    results = detector.detect(frame)
    frame_count += 1

    detected_count = 0
    filtered_count = 0
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]

        detected_count += 1
        # Filter weak detections
        if confidence < 0.3:
            filtered_count += 1
            continue

        # Filter irrelevant classes
        if label not in ALLOWED_CLASSES:
            filtered_count += 1
            continue

        detection_count += 1
        pixel_width = x2 - x1
        pixel_height = y2 - y1

        # Size & distance
        size = estimator.estimate_size(pixel_width)
        distance = estimator.estimate_distance(pixel_height)

        # Movement tracking
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        object_id = f"{label}_{int(center_x/50)}_{int(center_y/50)}"

        movement = "Static"
        if object_id in prev_positions:
            prev_x, prev_y = prev_positions[object_id]
            if abs(center_x - prev_x) > 5 or abs(center_y - prev_y) > 5:
                movement = "Moving"

        prev_positions[object_id] = (center_x, center_y)

        # Status logic
        if distance < 5:
            status = "CLOSE"
        elif distance < 15:
            status = "APPROACHING"
        else:
            status = "SAFE"

        label_text = f"{label.upper()} ({confidence*100:.0f}%) [{status}]"
        draw_overlay(frame, (x1, y1, x2, y2), label_text, size, distance)

    # Draw altitude
    draw_altitude(frame, ALTITUDE)

    # Crosshair
    h, w, _ = frame.shape
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255,255,255), 1)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255,255,255), 1)

    # Save frames where any boxes were drawn
    drawn = detected_count - filtered_count
    if drawn > 0:
        output_path = f"output/frame_{frame_count:04d}_drawn_{drawn}.jpg"
        cv2.imwrite(output_path, frame)
        print(f"✅ Frame {frame_count} saved (drawn={drawn}) → {output_path}")
    elif frame_count % 150 == 0:
        # periodic snapshots for context
        output_path = f"output/frame_{frame_count:04d}.jpg"
        cv2.imwrite(output_path, frame)
        print(f"ℹ️  Context frame {frame_count} saved → {output_path}")

cap.release()
print(f"\n📊 Summary:")
print(f"   Total frames: {frame_count}")
print(f"   Total detections: {detection_count}")
print(f"   Output saved to: output/")
