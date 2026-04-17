# estimator.py

KNOWN_PERSON_HEIGHT = 1.7  # meters

CALIBRATED = False
REAL_REF_WIDTH = 0.30  # laptop width (meters)
PIXEL_REF_WIDTH = None

# 👉 UPDATE THIS AFTER CALCULATING
FOCAL_LENGTH = 350  # calibrated value


class Estimator:

    @staticmethod
    def calibrate(pixel_width):
        global PIXEL_REF_WIDTH, CALIBRATED
        PIXEL_REF_WIDTH = pixel_width
        CALIBRATED = True
        print(f"📏 Calibration set: pixel width = {pixel_width}")

    @staticmethod
    def estimate_size(pixel_width):
        if CALIBRATED and PIXEL_REF_WIDTH:
            scale = REAL_REF_WIDTH / PIXEL_REF_WIDTH
            return pixel_width * scale
        else:
            return pixel_width * 0.002  # fallback

    @staticmethod
    def estimate_distance(pixel_height):
        if pixel_height == 0:
            return 0

        return (KNOWN_PERSON_HEIGHT * FOCAL_LENGTH) / pixel_height