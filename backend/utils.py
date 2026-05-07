import cv2


def get_color(distance):
    if distance < 5:
        return (0, 0, 255)
    elif distance < 15:
        return (0, 255, 255)
    else:
        return (0, 255, 0)


def draw_overlay(frame, box, label, size, distance):
    x1, y1, x2, y2 = map(int, box)

    color = get_color(distance)

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.rectangle(frame, (x1, y1 - 70), (x1 + 230, y1), color, -1)

    cv2.putText(frame, label, (x1 + 5, y1 - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.putText(frame, f"Size: {size:.2f} m", (x1 + 5, y1 - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.putText(frame, f"Dist: {distance:.1f} m", (x1 + 5, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)


def draw_altitude(frame, altitude):
    cv2.putText(frame, f"ALT: {altitude} m",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2)