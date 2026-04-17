# utils.py

import cv2


def get_color(distance):
    if distance < 5:
        return (0, 0, 255)      # RED
    elif distance < 15:
        return (0, 255, 255)    # YELLOW
    else:
        return (0, 255, 0)      # GREEN


def draw_overlay(frame, box, label, size, distance):
    x1, y1, x2, y2 = map(int, box)

    color = get_color(distance)

    # Bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # HUD panel
    cv2.rectangle(frame, (x1, y1 - 70), (x1 + 220, y1), color, -1)

    # Text
    cv2.putText(frame, label,
                (x1 + 5, y1 - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.putText(frame, f"Size: {size:.2f} m",
                (x1 + 5, y1 - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.putText(frame, f"Dist: {distance:.1f} m",
                (x1 + 5, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)