# tests/test_camera_thread.py
import numpy as np
from PyQt5.QtCore import QObject
from app.threads.camera_thread import CameraThread


class FakeCameraModel:
    def __init__(self):
        self.open_called = False
        self.release_called = False
        self.counter = 0

    def open(self):
        self.open_called = True

    def read(self):
        # 3번까지는 프레임 리턴, 그 다음부터는 None 리턴해서 쓰레드가 종료되도록
        if self.counter < 3:
            self.counter += 1
            return np.zeros((2, 2, 3), dtype=np.uint8)
        return None

    def release(self):
        self.release_called = True


class FrameReceiver(QObject):
    def __init__(self):
        super().__init__()
        self.frames = []

    def on_frame(self, frame):
        self.frames.append(frame)


def test_camera_thread_runs_and_emits(qtbot):
    camera_model = FakeCameraModel()
    thread = CameraThread(camera_model)
    receiver = FrameReceiver()

    thread.frame_ready.connect(receiver.on_frame)

    thread.start()

    # 쓰레드가 다 돌고 끝날 때까지 기다림
    qtbot.waitUntil(lambda: not thread.isRunning(), timeout=2000)

    assert camera_model.open_called
    assert camera_model.release_called
    assert len(receiver.frames) >= 1
