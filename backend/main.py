import cv2
from detector import ObjectDetector
from estimator import Estimator
from utils import draw_overlay

detector = ObjectDetector()
estimator = Estimator()

cap = cv2.VideoCapture(0)

prev_positions = {}

print("🚀 Press 'C' to calibrate using a known object")
print("❌ Press 'ESC' to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = detector.detect(frame)

    key = cv2.waitKey(1)

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]

        pixel_width = x2 - x1
        pixel_height = y2 - y1

        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]

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

        # Clean label
        label_text = f"{label.upper()} ({confidence*100:.0f}%) [{status}]"

        # Draw overlay
        draw_overlay(frame, (x1, y1, x2, y2), label_text, size, distance)

        # Calibration
        if key == ord('c'):
            estimator.calibrate(pixel_width)
            print("✅ Calibration done!")
            break

    # 🎯 Crosshair (Drone feel)
    h, w, _ = frame.shape
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255,255,255), 1)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255,255,255), 1)

    cv2.imshow("Drone UI Prototype", frame)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()