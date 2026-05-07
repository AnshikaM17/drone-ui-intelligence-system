from ultralytics import YOLO

class ObjectDetector:
    def __init__(self):
        # 🔥 Use better model for aerial scenes
        self.model = YOLO("yolov8m.pt")  # upgrade from n → m

    def detect(self, frame):
        results = self.model(frame)
        return results[0]