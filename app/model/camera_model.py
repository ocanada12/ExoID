# app/model/camera_model.py
import cv2


class CameraModel:
    """
    카메라 장치를 다루는 Model.
    실제 장치는 OpenCV VideoCapture를 사용하지만,
    테스트를 위해 capture_factory를 주입할 수 있게 설계.
    """

    def __init__(self, index=0, capture_factory=None):
        self.index = index
        self._capture_factory = capture_factory or (lambda i: cv2.VideoCapture(i))
        self.cap = None

    def open(self):
        if self.cap is None:
            self.cap = self._capture_factory(self.index)

    def is_opened(self):
        return self.cap is not None

    def read(self):
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
