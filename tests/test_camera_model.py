# tests/test_camera_model.py
import numpy as np
from app.model.camera_model import CameraModel


class FakeCapture:
    def __init__(self, index):
        self.index = index
        self.released = False
        self._counter = 0

    def read(self):
        # 처음 두 번은 프레임 리턴, 이후엔 실패
        if self._counter < 2:
            self._counter += 1
            frame = np.zeros((2, 2, 3), dtype=np.uint8)
            return True, frame
        return False, None

    def release(self):
        self.released = True


def fake_capture_factory(index):
    return FakeCapture(index)


def test_camera_model_open_read_release():
    cam = CameraModel(index=1, capture_factory=fake_capture_factory)

    assert not cam.is_opened()
    cam.open()
    assert cam.is_opened()

    frame1 = cam.read()
    assert frame1 is not None

    frame2 = cam.read()
    assert frame2 is not None

    # 더 이상 유효한 프레임 없음
    frame3 = cam.read()
    assert frame3 is None

    cam.release()
    assert not cam.is_opened()
