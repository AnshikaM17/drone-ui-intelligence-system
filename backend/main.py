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

cap = cv2.VideoCapture("../data/Rec_0009.mp4")

prev_positions = {}

ALLOWED_CLASSES = ["person", "car", "truck", "bus"]

print("🚀 Running on drone video...")
print("🖱️ Click 2 points to measure distance")
print("❌ Press ESC to exit")

# 🖱️ Enable mouse
cv2.namedWindow("Drone UI Prototype", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Drone UI Prototype", 1280, 720)
cv2.setMouseCallback("Drone UI Prototype", mouse_click)

# Try to move window to front (Windows-specific)
try:
    import win32gui
    hwnd = win32gui.FindWindow(None, "Drone UI Prototype")
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
except:
    pass

while True:
    ret, frame = cap.read()
    if not ret:
        print("🎬 Video ended")
        break

    results = detector.detect(frame)

    detected_count = 0
    filtered_count = 0

    for box in results.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        confidence = float(box.conf[0])
        label = results.names[int(box.cls[0])]

        detected_count += 1

        # 🔴 Filter weak detections (lowered threshold for better detection)
        if confidence < 0.3:
            filtered_count += 1
            continue

        # 🔴 Filter irrelevant classes
        if label not in ALLOWED_CLASSES:
            filtered_count += 1
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

    # Debug info
    if detected_count > 0:
        print(f"Frame: Detected={detected_count}, Filtered={filtered_count}, Drawn={detected_count-filtered_count}")

    cv2.imshow("Drone UI Prototype", frame)

    # Wait 100ms (slower playback) and check for ESC key
    try:
        if cv2.waitKey(100) == 27:
            break
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        break

cap.release()
print("\n⏸️  Window will close in 5 seconds...")
cv2.waitKey(5000)  # Keep window open for 5 seconds
cv2.destroyAllWindows()