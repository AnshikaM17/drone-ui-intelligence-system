from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path="models/yolov8n.pt"):
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        results = self.model(frame)
        return results[0]
    