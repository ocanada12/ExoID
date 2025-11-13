# app/view/main_view.py
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)

        ui_path = Path(__file__).resolve().parent.parent / "ui" / "main_window.ui"
        loadUi(str(ui_path), self)

        self.controller = controller

        # 버튼 시그널 연결
        self.startButton.clicked.connect(self.controller.handle_start)
        self.stopButton.clicked.connect(self.controller.handle_stop)

        # 초기 라벨 텍스트
        self.sumLabel.setText("0")

    # --- Controller에서 호출하는 View 업데이트 함수 ---

    def update_sum_label(self, value: int):
        self.sumLabel.setText(str(value))

    def update_video_label(self, frame):
        """
        frame: numpy ndarray (BGR)
        """
        if frame is None:
            return

        frame_bgr = np.asarray(frame)
        if frame_bgr.ndim != 3:
            return

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        # 라벨 크기에 맞게 스케일링 (원하면 생략 가능)
        pixmap = pixmap.scaled(self.videoLabel.width(), self.videoLabel.height())
        self.videoLabel.setPixmap(pixmap)
