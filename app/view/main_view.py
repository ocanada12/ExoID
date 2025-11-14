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

    def update_progress(self, value):
        self.progressBar.setValue(int(value))

    def update_video_label(self, frame, roi_rect=None, water_y=None):
        """
        frame: numpy ndarray (BGR)
        roi_rect: (x, y, w, h) 또는 None
        water_y: int 또는 None (프레임 전체 기준 y좌표)
        """
        if frame is None:
            return

        disp = frame.copy()

        # --- ROI 노란 박스 ---
        if roi_rect is not None:
            x, y, w, h = roi_rect
            # 노란색 (BGR: 0,255,255)
            cv2.rectangle(disp, (x, y), (x + w, y + h), (0, 255, 255), 2)

            # --- 수면 레벨 초록 선 (ROI 안에서만 표시) ---
            if water_y is not None:
                y_line = int(water_y)
                y_line = max(y, min(y + h - 1, y_line))
                # 초록색 (BGR: 0,255,0)
                cv2.line(disp, (x, y_line), (x + w, y_line), (0, 255, 0), 2)

        frame_rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(q_img)
        pixmap = pixmap.scaled(self.videoLabel.width(), self.videoLabel.height())
        self.videoLabel.setPixmap(pixmap)