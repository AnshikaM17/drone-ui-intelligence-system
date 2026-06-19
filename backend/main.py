# main.py
# ─────────────────────────────────────────────────────────────────
# Main pipeline for the Drone UI Intelligence System.
# Supports:
#   python main.py                       → live webcam (device 0)
#   python main.py --source <path>       → video file / image / folder
#   python main.py --source 0            → explicit webcam
# ─────────────────────────────────────────────────────────────────

import cv2
import sys
import os
import argparse
import time
from detector import ObjectDetector
from estimator import Estimator
from utils import draw_overlay, draw_scale_bar, draw_status_strip
from config import GLOBAL_MIN_CONFIDENCE, MIN_CONFIDENCE_PER_CLASS, FOCAL_LENGTH_PX, ALTITUDE

# ── Argument parsing ──────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Drone UI Intelligence System")
parser.add_argument(
    "--source",
    type=str,
    default="0",
    help="Input source: 0 for webcam, or path to a video/image file"
)
parser.add_argument(
    "--output",
    type=str,
    default=None,
    help="Optional: path to save the processed output video (e.g. output.mp4)"
)
parser.add_argument(
    "--duration",
    type=int,
    default=0,
    help="Optional: auto-exit after this many seconds (useful for demo clips). 0 = run until ESC."
)
args = parser.parse_args()

# ── Resolve source ────────────────────────────────────────────────
source = args.source
if source.isdigit():
    source = int(source)   # webcam index

# ── Initialise components ─────────────────────────────────────────
detector  = ObjectDetector()
estimator = Estimator()

cap = cv2.VideoCapture(source)

if not cap.isOpened():
    print(f"❌ Could not open source: {source}")
    sys.exit(1)

# ── Video writer (optional output saving) ─────────────────────────
writer = None
if args.output:
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
    print(f"💾 Saving output to: {args.output}")

# ── Stats & FPS tracker ───────────────────────────────────────────
total_frames   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps_src        = cap.get(cv2.CAP_PROP_FPS) or 25
duration_sec   = total_frames / fps_src if total_frames > 0 else 0
_fps_t0        = time.time()
_fps_count     = 0
_live_fps      = 0.0
start_time     = time.time()

print("🚀 Drone UI Intelligence System started")
print(f"   Source  : {source}")
if total_frames > 0:
    print(f"   Frames  : {total_frames}  ({duration_sec:.1f} s @ {fps_src:.1f} fps)")
print("   Press  C    →  calibrate using detected object's pixel width")
print("   Press  ESC  →  exit")
print("   Press  SPACE→  pause / resume")
print("   Left-click & drag  →  measure real-world distance between two points")
print("   Right-click        →  clear the measurement ruler")
print()

# ── Tracking state ─────────────────────────────────────────────
prev_positions: dict = {}
paused = False
frame_count = 0

# ── Mouse Measuring Tool state ───────────────────────────────
# Left-click  → set start point
# Hold & drag → live preview of the measurement line
# Release      → finalise and display real-world distance
measure_start  = None   # (x, y) pixel coords of first click
measure_end    = None   # (x, y) pixel coords of release / current drag
measure_active = False  # True while mouse button is held

def mouse_callback(event, x, y, flags, param):
    global measure_start, measure_end, measure_active
    if event == cv2.EVENT_LBUTTONDOWN:
        measure_start  = (x, y)
        measure_end    = (x, y)
        measure_active = True
    elif event == cv2.EVENT_MOUSEMOVE and measure_active:
        measure_end = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        measure_end    = (x, y)
        measure_active = False
    elif event == cv2.EVENT_RBUTTONDOWN:   # right-click clears the ruler
        measure_start  = None
        measure_end    = None
        measure_active = False

# ── Main loop ─────────────────────────────────────────────
WIN_NAME = "Drone UI Intelligence System"
cv2.namedWindow(WIN_NAME)
cv2.setMouseCallback(WIN_NAME, mouse_callback)

while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            print("\n✅ End of video reached.")
            break
        frame_count += 1

    # ── Key handling (outside box loop — once per frame) ──────────
    key = cv2.waitKey(1) & 0xFF

    if key == 27:          # ESC → quit
        print("\n🛑 Exited by user.")
        break
    elif key == ord(' '):  # SPACE → pause / resume
        paused = not paused
        status_str = "⏸ Paused" if paused else "▶ Resumed"
        print(f"\r{status_str}  ", end="", flush=True)
        continue

    if paused:
        cv2.imshow(WIN_NAME, frame)
        continue

    # ── Detection ─────────────────────────────────────────────────
    results = detector.detect(frame)

    calibration_triggered = False
    # Collect drawn boxes for semantic ruler context
    drawn_boxes = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0]

        pixel_width  = float(x2 - x1)
        pixel_height = float(y2 - y1)

        confidence = float(box.conf[0])
        label      = results.names[int(box.cls[0])]

        # ── Confidence filter (suppresses false positives e.g. house→train) ─
        min_conf = MIN_CONFIDENCE_PER_CLASS.get(label, GLOBAL_MIN_CONFIDENCE)
        if confidence < min_conf:
            continue

        # ── Calibration trigger (once per frame) ──────────────────
        if (key == ord('c') or key == ord('C')) and not calibration_triggered:
            estimator.calibrate(pixel_width)
            calibration_triggered = True

        # ── Size & Distance (physics-based, per-class) ────────────
        size     = estimator.estimate_size(pixel_width,  label)
        distance = estimator.estimate_distance(pixel_height, label)

        # ── Movement tracking ─────────────────────────────────────
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        object_id = f"{label}_{int(center_x / 50)}_{int(center_y / 50)}"

        movement = "Static"
        if object_id in prev_positions:
            prev_x, prev_y = prev_positions[object_id]
            if abs(center_x - prev_x) > 5 or abs(center_y - prev_y) > 5:
                movement = "Moving"
        prev_positions[object_id] = (center_x, center_y)

        # ── Status classification ─────────────────────────────────
        if distance < 5:
            status = "CLOSE"
        elif distance < 15:
            status = "APPROACHING"
        else:
            status = "SAFE"

        label_text = f"{label.upper()} ({confidence * 100:.0f}%) [{status}]"
        draw_overlay(frame, (x1, y1, x2, y2), label_text, size, distance)
        drawn_boxes.append((label, size, x1, y1, x2, y2))

    # ── Mouse Measuring Tool overlay ──────────────────────────────
    if measure_start and measure_end:
        px1, py1 = measure_start
        px2, py2 = measure_end
        pixel_dist = ((px2 - px1) ** 2 + (py2 - py1) ** 2) ** 0.5
        from config import FOCAL_LENGTH_PX, ALTITUDE
        real_m = (pixel_dist / FOCAL_LENGTH_PX) * ALTITUDE

        # ── Semantic context: express distance in real-world object units ──
        semantic = ""
        if drawn_boxes:
            # Use the first drawn object as semantic reference
            ref_label, ref_size, *_ = drawn_boxes[0]
            if ref_size > 0.1:
                ratio = real_m / ref_size
                semantic = f"  ≈{ratio:.1f} {ref_label} widths"
        elif real_m > 0:
            # Fallback: compare to common references
            if real_m < 2:
                semantic = f"  ≈ door width"
            elif real_m < 5:
                semantic = f"  ≈ car length"
            elif real_m < 12:
                semantic = f"  ≈ bus length"
            else:
                semantic = f"  ≈ {real_m/3.0:.0f} storeys"

        RULER_COLOR  = (0, 230, 230)
        SHADOW_COLOR = (0, 0, 0)

        cv2.line(frame, (px1, py1), (px2, py2), SHADOW_COLOR, 5, cv2.LINE_AA)
        cv2.line(frame, (px1, py1), (px2, py2), RULER_COLOR, 2, cv2.LINE_AA)

        for pt in [measure_start, measure_end]:
            cv2.circle(frame, pt, 9,  SHADOW_COLOR, -1)
            cv2.circle(frame, pt, 8,  RULER_COLOR,  2)
            cv2.circle(frame, pt, 3,  RULER_COLOR,  -1)

        import math
        dx = px2 - px1
        dy = py2 - py1
        length = max(pixel_dist, 1)
        nx, ny = -dy / length, dx / length
        tick = 8
        for pt in [(px1, py1), (px2, py2)]:
            tx = int(pt[0] + nx * tick)
            ty = int(pt[1] + ny * tick)
            bx = int(pt[0] - nx * tick)
            by = int(pt[1] - ny * tick)
            cv2.line(frame, (tx, ty), (bx, by), SHADOW_COLOR, 4, cv2.LINE_AA)
            cv2.line(frame, (tx, ty), (bx, by), RULER_COLOR,  2, cv2.LINE_AA)

        mid_x = (px1 + px2) // 2
        mid_y = (py1 + py2) // 2
        label_m = f"  {real_m:.1f} m  |  {int(pixel_dist)} px{semantic}  "
        font_face  = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.65
        font_thick = 1
        (tw, th), baseline = cv2.getTextSize(label_m, font_face, font_scale, font_thick)
        pad = 5
        cv2.rectangle(frame,
                       (mid_x - tw // 2 - pad,     mid_y - th - pad - 2),
                       (mid_x + tw // 2 + pad,     mid_y + baseline + pad),
                       (20, 20, 20), -1, cv2.LINE_AA)
        cv2.rectangle(frame,
                       (mid_x - tw // 2 - pad,     mid_y - th - pad - 2),
                       (mid_x + tw // 2 + pad,     mid_y + baseline + pad),
                       RULER_COLOR, 1, cv2.LINE_AA)
        cv2.putText(frame, label_m,
                    (mid_x - tw // 2 + 1, mid_y + 1),
                    font_face, font_scale, SHADOW_COLOR, font_thick + 1, cv2.LINE_AA)
        cv2.putText(frame, label_m,
                    (mid_x - tw // 2, mid_y),
                    font_face, font_scale, RULER_COLOR, font_thick, cv2.LINE_AA)

    # ── Crosshair ────────────────────────────────────────────────
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    for off in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        cv2.line(frame, (cx - 25 + off[0], cy + off[1]), (cx + 25 + off[0], cy + off[1]), (0, 0, 0), 1)
        cv2.line(frame, (cx + off[0], cy - 25 + off[1]), (cx + off[0], cy + 25 + off[1]), (0, 0, 0), 1)
    cv2.line(frame, (cx - 25, cy), (cx - 6, cy), (255, 255, 255), 1, cv2.LINE_AA)
    cv2.line(frame, (cx + 6,  cy), (cx + 25, cy), (255, 255, 255), 1, cv2.LINE_AA)
    cv2.line(frame, (cx, cy - 25), (cx, cy - 6),  (255, 255, 255), 1, cv2.LINE_AA)
    cv2.line(frame, (cx, cy + 6),  (cx, cy + 25), (255, 255, 255), 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), 3, (255, 255, 255), 1, cv2.LINE_AA)

    # ── Scale bar + Status strip ──────────────────────────────────
    draw_scale_bar(frame, FOCAL_LENGTH_PX, ALTITUDE)
    draw_status_strip(frame, ALTITUDE, FOCAL_LENGTH_PX, _live_fps, paused)

    # ── FPS counter ───────────────────────────────────────────────
    _fps_count += 1
    if _fps_count >= 15:
        _live_fps  = _fps_count / (time.time() - _fps_t0)
        _fps_t0    = time.time()
        _fps_count = 0

    # ── Auto-exit after --duration seconds ────────────────────────
    if args.duration > 0 and (time.time() - start_time) >= args.duration:
        print(f"\n⏹ Auto-exit after {args.duration}s demo clip.")
        break

    # ── Progress bar strip (bottom of frame) ───────────────────────
    if total_frames > 0:
        bar_h  = 14
        fill_w = int(w * frame_count / total_frames)
        cv2.rectangle(frame, (0, h - bar_h), (w, h), (20, 20, 20), -1)
        cv2.rectangle(frame, (0, h - bar_h), (fill_w, h), (50, 200, 80), -1)
        pct_str = f"{frame_count / total_frames * 100:.1f}%  {frame_count}/{total_frames}"
        cv2.putText(frame, pct_str, (6, h - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)

    # ── Display & Save ────────────────────────────────────────────
    cv2.imshow(WIN_NAME, frame)
    if writer:
        writer.write(frame)

    # ── Progress in terminal ──────────────────────────────────────
    if total_frames > 0 and frame_count % 30 == 0:
        pct = frame_count / total_frames * 100
        print(f"\r⏳ Progress: {pct:.1f}%  ({frame_count}/{total_frames} frames)", end="", flush=True)

# ── Cleanup ───────────────────────────────────────────────────────
cap.release()
if writer:
    writer.release()
    print(f"\n💾 Output saved to: {args.output}")
cv2.destroyAllWindows()
