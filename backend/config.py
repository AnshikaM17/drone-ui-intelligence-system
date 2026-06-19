# config.py
# ─────────────────────────────────────────────────────────────────
# Central configuration for the Drone UI Intelligence System.
# All physical constants, camera parameters, and class-specific
# known dimensions are defined here so they can be adjusted in
# one place without touching estimation logic.
# ─────────────────────────────────────────────────────────────────

# ── Camera / Sensor Parameters ────────────────────────────────────
# Focal length in PIXELS.
# Derive with:  F = (P × D) / W
#   P = pixel width of reference object at distance D
#   D = known real-world distance (metres)
#   W = known real-world width of reference object (metres)
# Default calibrated for a standard 640×480 webcam at ~1 m distance.
FOCAL_LENGTH_PX = 700       # pixels  (single source of truth)

IMAGE_WIDTH  = 640          # pixels – frame width
IMAGE_HEIGHT = 480          # pixels – frame height

# ── Drone / Camera Altitude ───────────────────────────────────────
# Altitude in metres.  Replace with live MAVLink telemetry later.
ALTITUDE = 10               # metres (simulated)

# ── Sensor dimensions (for reference only, not used in MVP math) ──
SENSOR_WIDTH_MM  = 6.4      # mm
SENSOR_HEIGHT_MM = 4.8      # mm

# ─────────────────────────────────────────────────────────────────
# Known Real-World Object Dimensions  (metres)
# ─────────────────────────────────────────────────────────────────
# These are average values used when no per-instance calibration
# is available.  Both HEIGHT and WIDTH are stored so the estimator
# can choose the appropriate dimension to match the bounding-box
# axis it measures.
#
# Distance formula uses HEIGHT  (vertical, more stable from above)
# Size    formula uses WIDTH    (horizontal extent)
# ─────────────────────────────────────────────────────────────────
KNOWN_DIMENSIONS = {
    # class label       : (real_height_m, real_width_m)
    "person"            : (1.70, 0.50),
    "car"               : (1.50, 4.50),   # sedan – height from ground to roof
    "truck"             : (3.50, 8.00),
    "bus"               : (3.20, 12.00),
    "bicycle"           : (1.10, 1.80),
    "motorcycle"        : (1.20, 2.20),
    "dog"               : (0.55, 0.80),
    "cat"               : (0.30, 0.45),
    "backpack"          : (0.50, 0.30),
    "handbag"           : (0.35, 0.25),
    # ── fallback when class not listed ───────────────────────────
    "__default__"       : (1.70, 0.50),   # treat unknown as person-sized
}

# ── Calibration Reference Object ─────────────────────────────────
# The object used when the user presses 'C' to manually calibrate.
# Change this to whatever you're holding up in front of the camera.
CALIBRATION_REF_WIDTH_M = 0.30   # metres  (e.g. a standard laptop lid width)

# ── Detection Confidence Thresholds ──────────────────────────────
# Global minimum confidence — detections below this are always dropped.
GLOBAL_MIN_CONFIDENCE = 0.40

# Per-class overrides — raise the bar for classes that frequently
# appear as false positives in aerial/drone footage.
# Houses, rooftops and shadows are commonly misclassified as 'train'
# or 'bus' at low confidence; requiring ≥0.70 eliminates most of these.
MIN_CONFIDENCE_PER_CLASS = {
    "train"     : 0.82,   # very high bar — rooftops/roads constantly mislabelled as train
    "bus"       : 0.70,   # elevated threshold — large rectangles trigger bus
    "boat"      : 0.70,   # water reflections / rooftops trigger boat
    "airplane"  : 0.75,   # rare in drone footage; needs high confidence
    "kite"      : 0.65,
}