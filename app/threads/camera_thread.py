# app/threads/camera_thread.py
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np


class CameraThread(QThread):
    frame_ready = pyqtSignal(object)  # np.ndarray

    def __init__(self, camera_model, parent=None):
        super().__init__(parent)
        self.camera_model = camera_model
        self._running = False

    def run(self):
        self._running = True
        self.camera_model.open()
        while self._running:
            frame = self.camera_model.read()
            if frame is None:
                break
            # frame은 numpy ndarray 라고 가정
            self.frame_ready.emit(frame)
            self.msleep(30)  # 약 30ms 간격(약 30fps)

        self.camera_model.release()

    def stop(self):
        self._running = False
