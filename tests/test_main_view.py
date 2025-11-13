# tests/test_main_view.py
import numpy as np
from PyQt5.QtCore import Qt
from app.view.main_view import MainWindow


class DummyController:
    def __init__(self):
        self.start_called = False
        self.stop_called = False

    def handle_start(self):
        self.start_called = True

    def handle_stop(self):
        self.stop_called = True


def test_main_window_update_labels(qtbot):
    controller = DummyController()
    window = MainWindow(controller=controller)
    qtbot.addWidget(window)

    # sumLabel 업데이트 확인
    window.update_sum_label(123)
    assert window.sumLabel.text() == "123"

    # videoLabel에 프레임 그리기 확인
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    window.resize(200, 200)
    qtbot.wait(10)  # 레이아웃 계산 약간 기다리기
    window.update_video_label(frame)
    assert window.videoLabel.pixmap() is not None


def test_main_window_buttons_call_controller(qtbot):
    controller = DummyController()
    window = MainWindow(controller=controller)
    qtbot.addWidget(window)

    # Start / Stop 버튼 클릭 시 컨트롤러 메서드가 호출되는지 확인
    qtbot.mouseClick(window.startButton, Qt.LeftButton)
    qtbot.mouseClick(window.stopButton, Qt.LeftButton)

    assert controller.start_called
    assert controller.stop_called
