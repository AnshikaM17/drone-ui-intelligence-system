import cv2
from detector import ObjectDetector
from estimator import Estimator, ALTITUDE
from utils import draw_overlay, draw_altitude

# 🖱️ Store clicked points
points = []

def mouse_click(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

        # Keep only last 2 points
        if len(points) > 2:
            points.pop(0)


detector = ObjectDetector()
estimator = Estimator()

cap = cv2.VideoCapture("data/Rec_0009.mp4")

prev_positions = {}

ALLOWED_CLASSES = ["person", "car", "truck", "bus"]

print("🚀 Running on drone video...")
print("🖱️ Click 2 points to measure distance")
print("❌ Press ESC to exit")

# 🖱️ Enable mouse
cv2.namedWindow("Drone UI Prototype")
cv2.setMouseCallback("Drone UI Prototype", mouse_click)

while True:
    ret, frame = cap.read()
    if not ret:
        print("🎬 Video ended")
        break

    results = detector.detect(frame)

    key = cv2.waitKey(30)

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]

        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]

        # 🔴 Filter weak detections
        if confidence < 0.5:
            continue

        # 🔴 Filter irrelevant classes
        if label not in ALLOWED_CLASSES:
            continue

        pixel_width = x2 - x1
        pixel_height = y2 - y1

        # 📏 Size & distance
        size = estimator.estimate_size(pixel_width)
        distance = estimator.estimate_distance(pixel_height)

        # 🚶 Movement tracking
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        object_id = f"{label}_{int(center_x/50)}_{int(center_y/50)}"

        movement = "Static"
        if object_id in prev_positions:
            prev_x, prev_y = prev_positions[object_id]
            if abs(center_x - prev_x) > 5 or abs(center_y - prev_y) > 5:
                movement = "Moving"

        prev_positions[object_id] = (center_x, center_y)

        # ⚠️ Status logic
        if distance < 5:
            status = "CLOSE"
        elif distance < 15:
            status = "APPROACHING"
        else:
            status = "SAFE"

        label_text = f"{label.upper()} ({confidence*100:.0f}%) [{status}]"

        draw_overlay(frame, (x1, y1, x2, y2), label_text, size, distance)

    # 📏 DRAW MEASUREMENT LINE (UPDATED - CORRECT METHOD)
    if len(points) == 2:
        p1, p2 = points

        # Draw line
        cv2.line(frame, p1, p2, (255, 255, 0), 2)

        # ✅ Use estimator (correct math)
        dist = estimator.pixel_to_real_distance(p1, p2, frame.shape[1])

        # Display distance
        cv2.putText(frame, f"{dist:.2f} m",
                    (p1[0], p1[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255,255,0), 2)

    # 📡 Altitude display
    draw_altitude(frame, ALTITUDE)

    # 🎯 Crosshair
    h, w, _ = frame.shape
    cv2.line(frame, (w//2 - 20, h//2), (w//2 + 20, h//2), (255,255,255), 1)
    cv2.line(frame, (w//2, h//2 - 20), (w//2, h//2 + 20), (255,255,255), 1)

    cv2.imshow("Drone UI Prototype", frame)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()