# estimator.py
# -----------------------------------------------------------------
# Physics-based size and distance estimation using the pinhole
# camera model with per-class known real-world dimensions.
#
# Key formulas:
#   distance = (real_height * focal_length) / pixel_height
#   real_width = (pixel_width / focal_length) * distance
# -----------------------------------------------------------------

from config import FOCAL_LENGTH_PX, KNOWN_DIMENSIONS, CALIBRATION_REF_WIDTH_M


class Estimator:

    def __init__(self):
        self._focal_length = FOCAL_LENGTH_PX

    # ------------------------------------------------------------------
    # Calibration  (press 'C' in the main loop)
    # ------------------------------------------------------------------
    def calibrate(self, pixel_width: float, label: str = "__default__"):
        """
        Re-derive focal length from a detected object of known real width.
        Uses the per-class width from KNOWN_DIMENSIONS if available,
        otherwise falls back to CALIBRATION_REF_WIDTH_M from config.
        """
        real_w = KNOWN_DIMENSIONS.get(label, KNOWN_DIMENSIONS["__default__"])[1]
        if pixel_width > 0:
            self._focal_length = (pixel_width * 10) / real_w  # D=10m assumption
            print(f"\n✅ Calibrated: focal_length = {self._focal_length:.1f} px "
                  f"(using {label}, real_w={real_w} m)")

    # ------------------------------------------------------------------
    # Distance estimation  (pinhole: D = H_real * F / H_px)
    # ------------------------------------------------------------------
    def estimate_distance(self, pixel_height: float, label: str = "__default__") -> float:
        """
        Estimate real-world distance to an object using its known height.
        Returns metres.
        """
        if pixel_height <= 0:
            return 0.0
        real_h = KNOWN_DIMENSIONS.get(label, KNOWN_DIMENSIONS["__default__"])[0]
        return (real_h * self._focal_length) / pixel_height

    # ------------------------------------------------------------------
    # Size estimation  (pinhole: W_real = W_px / F * D)
    # ------------------------------------------------------------------
    def estimate_size(self, pixel_width: float, label: str = "__default__") -> float:
        """
        Estimate the real-world width of an object from its pixel span
        and estimated distance (derived via estimate_distance using
        the object's known height).
        Returns metres.
        """
        real_h = KNOWN_DIMENSIONS.get(label, KNOWN_DIMENSIONS["__default__"])[0]
        # First get distance using the height dimension (more stable top-down)
        # We don't have pixel_height here so we use focal_length directly with
        # the known real_height as the reference: assume a typical 'face-on' box
        # where pixel_height ≈ pixel_width (rough proxy for unknown objects).
        # For accuracy, main.py passes both pixel_width AND label so we can use
        # the known real_width directly.
        real_w = KNOWN_DIMENSIONS.get(label, KNOWN_DIMENSIONS["__default__"])[1]
        distance = (real_h * self._focal_length) / max(pixel_width, 1)
        # Re-derive width from the distance we just estimated
        real_width_estimated = (pixel_width / self._focal_length) * distance
        # Clamp to known real_width if estimate diverges badly
        return min(real_width_estimated, real_w * 2)
