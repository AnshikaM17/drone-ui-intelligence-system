import math

# 📡 Simulated telemetry
ALTITUDE = 25  # meters (adjusted for better accuracy from drone height)

KNOWN_PERSON_HEIGHT = 1.7  # meters

CALIBRATED = False
REAL_REF_WIDTH = 1.8  # meters - Updated for vehicle calibration (standard car width)
PIXEL_REF_WIDTH = None

FOCAL_LENGTH = 350


class Estimator:

    @staticmethod
    def calibrate(pixel_width):
        global PIXEL_REF_WIDTH, CALIBRATED
        PIXEL_REF_WIDTH = pixel_width
        CALIBRATED = True

    @staticmethod
    def estimate_size(pixel_width):
        if CALIBRATED and PIXEL_REF_WIDTH:
            scale = REAL_REF_WIDTH / PIXEL_REF_WIDTH
            return pixel_width * scale
        else:
            return pixel_width * 0.002

    @staticmethod
    def estimate_distance(pixel_height):
        if pixel_height == 0:
            return 0
        return (KNOWN_PERSON_HEIGHT * FOCAL_LENGTH) / pixel_height

    # 🔥 NEW: Pixel → real-world conversion using altitude
    @staticmethod
    def pixel_to_real_distance(p1, p2, frame_width=640):
        pixel_dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

        # 🎯 Ground coverage approximation
        # Assume camera horizontal field of view ≈ 70 degrees
        FOV = 70  

        # Ground width covered by camera
        ground_width = 2 * ALTITUDE * math.tan(math.radians(FOV / 2))

        # meters per pixel
        meters_per_pixel = ground_width / frame_width

        return pixel_dist * meters_per_pixel