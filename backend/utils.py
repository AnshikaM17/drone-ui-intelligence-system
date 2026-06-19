# utils.py
# -----------------------------------------------------------------
# HUD / Overlay rendering for the Drone UI Intelligence System.
#
# Functions:
#   get_color(distance)          - threat colour by distance
#   draw_overlay(...)            - per-object bounding box + info panel
#   draw_scale_bar(...)          - real-world reference ruler on frame
#   draw_status_strip(...)       - top telemetry bar
# -----------------------------------------------------------------

import cv2
import numpy as np


# ── Threat colour (BGR) ───────────────────────────────────────────
def get_color(distance):
    if distance < 5:
        return (0, 60, 255)       # vivid red    – CLOSE
    elif distance < 15:
        return (0, 200, 255)      # vivid amber  – APPROACHING
    else:
        return (50, 220, 50)      # vivid green  – SAFE


def _put_shadowed(frame, text, pos, font, scale, color, thick=1):
    """White-outlined text for legibility on any background."""
    x, y = pos
    cv2.putText(frame, text, (x + 1, y + 1), font, scale, (0, 0, 0), thick + 1, cv2.LINE_AA)
    cv2.putText(frame, text, pos,             font, scale, color,     thick,     cv2.LINE_AA)


def _corner_brackets(frame, x1, y1, x2, y2, color, thick=2, arm=18):
    """Tactical corner-bracket bounding box."""
    pts = [
        ((x1, y1), (x1 + arm, y1)), ((x1, y1), (x1, y1 + arm)),
        ((x2, y1), (x2 - arm, y1)), ((x2, y1), (x2, y1 + arm)),
        ((x1, y2), (x1 + arm, y2)), ((x1, y2), (x1, y2 - arm)),
        ((x2, y2), (x2 - arm, y2)), ((x2, y2), (x2, y2 - arm)),
    ]
    for p1, p2 in pts:
        cv2.line(frame, p1, p2, color, thick, cv2.LINE_AA)
    # faint full-rect outline
    ov = frame.copy()
    cv2.rectangle(ov, (x1, y1), (x2, y2), color, 1)
    cv2.addWeighted(ov, 0.20, frame, 0.80, 0, frame)


# ── Per-object overlay ────────────────────────────────────────────
def draw_overlay(frame, box, label, size, distance):
    x1, y1, x2, y2 = map(int, box)
    color = get_color(distance)

    # Corner-bracket bounding box
    _corner_brackets(frame, x1, y1, x2, y2, color)

    # Centre dot
    cv2.circle(frame, ((x1 + x2) // 2, (y1 + y2) // 2), 3, color, -1)

    # Semi-transparent info panel
    font       = cv2.FONT_HERSHEY_DUPLEX
    fscale     = 0.50
    fthick     = 1
    line_h     = 21
    pad        = 6
    rows = [label, f"Size : {size:.2f} m", f"Dist : {distance:.1f} m"]
    max_w = max(cv2.getTextSize(r, font, fscale, fthick)[0][0] for r in rows)
    pw = max_w + pad * 2
    ph = line_h * len(rows) + pad * 2

    # Place above box; flip below if clipped
    if y1 - ph - 4 >= 0:
        py1, py2 = y1 - ph - 4, y1 - 4
    else:
        py1, py2 = y2 + 4, y2 + ph + 4

    ov = frame.copy()
    cv2.rectangle(ov, (x1, py1), (x1 + pw, py2), (10, 10, 10), -1)
    cv2.addWeighted(ov, 0.75, frame, 0.25, 0, frame)
    cv2.rectangle(frame, (x1, py1), (x1 + pw, py1 + 2), color, -1)  # top border

    tx = x1 + pad
    for i, row in enumerate(rows):
        ty = py1 + pad + line_h * (i + 1) - 2
        c  = color if i == 0 else (220, 220, 220)
        _put_shadowed(frame, row, (tx, ty), font, fscale, c, fthick)


# ── Scale bar  (semantically scaled reference ruler) ─────────────
def draw_scale_bar(frame, focal_length_px: float, altitude_m: float,
                   ref_metres: float = 10.0):
    """
    Draws a real-world reference scale bar in the bottom-right corner.

    Formula:
        meters_per_pixel = altitude / focal_length
        bar_px = ref_metres / meters_per_pixel = ref_metres * focal_length / altitude

    This directly shows the viewer how far 10 m (or chosen ref) stretches
    in the current frame — the core of 'semantically scaled measurement'.
    """
    h, w = frame.shape[:2]
    mpp = altitude_m / focal_length_px          # metres per pixel
    bar_px = int(ref_metres / mpp)
    bar_px = max(30, min(bar_px, w // 3))       # clamp for readability

    margin  = 16
    bar_y   = h - 30
    bar_x2  = w - margin
    bar_x1  = bar_x2 - bar_px

    # Shadow + bright bar
    cv2.line(frame, (bar_x1, bar_y), (bar_x2, bar_y), (0, 0, 0),       4, cv2.LINE_AA)
    cv2.line(frame, (bar_x1, bar_y), (bar_x2, bar_y), (80, 255, 180),   2, cv2.LINE_AA)
    # End ticks
    for x in [bar_x1, bar_x2]:
        cv2.line(frame, (x, bar_y - 5), (x, bar_y + 5), (80, 255, 180), 2, cv2.LINE_AA)

    label = f"= {ref_metres:.0f} m"
    (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
    lx = bar_x1 + (bar_px - tw) // 2
    _put_shadowed(frame, label, (lx, bar_y - 8),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.42, (80, 255, 180), 1)


# ── Top telemetry status strip ────────────────────────────────────
def draw_status_strip(frame, altitude_m: float, focal_length_px: float,
                      fps: float = 0.0, paused: bool = False):
    """
    Draws a translucent top bar showing:
      ALT | FOCAL | m/px resolution | FPS | PAUSED flag
    """
    h, w = frame.shape[:2]
    strip_h = 26
    mpp = altitude_m / focal_length_px

    ov = frame.copy()
    cv2.rectangle(ov, (0, 0), (w, strip_h), (10, 10, 10), -1)
    cv2.addWeighted(ov, 0.65, frame, 0.35, 0, frame)

    items = [
        f"ALT {altitude_m:.0f} m",
        f"F {focal_length_px:.0f} px",
        f"{mpp:.3f} m/px",
    ]
    if fps > 0:
        items.append(f"{fps:.1f} FPS")
    if paused:
        items.append("⏸ PAUSED")

    font   = cv2.FONT_HERSHEY_SIMPLEX
    fscale = 0.40
    x      = 8
    for item in items:
        _put_shadowed(frame, item, (x, strip_h - 7), font, fscale, (180, 255, 180), 1)
        tw, _ = cv2.getTextSize(item, font, fscale, 1)[0]
        x += tw + 18
        cv2.line(frame, (x - 9, 5), (x - 9, strip_h - 5), (60, 60, 60), 1)
