# app/services/video_analyzer.py
import numpy as np
import cv2


class VideoAnalyzer:
    """
    영상 분석을 담당하는 별도 모듈.
    여기서 ROI 분석, threshold, 수면 레벨 등 다 확장 가능.
    지금은 '픽셀 총합'만 계산.
    """
    def __init__(self, protocol_config=None):
        self.config = protocol_config


    def calculate_sum(self, frame) -> int:
        """
        frame: numpy ndarray (BGR or Gray)
        return: 픽셀 값 총합 (int)
        """
        if frame is None:
            return 0

        arr = np.asarray(frame)
        if arr.ndim == 3:
            # BGR → Gray
            gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        else:
            gray = arr

        return int(np.sum(gray))


    def analyze(self, frame):
        """
        frame: numpy ndarray (BGR 또는 gray)
        return: (pixel_sum, roi_rect, water_y)

        - pixel_sum: 전체 프레임 픽셀 총합
        - roi_rect: (x, y, w, h) 중앙 ROI 위치 (프레임 좌표)
        - water_y: 프레임 좌표계에서 수면 레벨(y 값)
        """
        if frame is None:
            return 0, None, None

        arr = np.asarray(frame)
        if arr.ndim == 3:
            gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        else:
            gray = arr

        h, w = gray.shape[:2]
        pixel_sum = int(np.sum(gray))

        # --- 중앙 100x100 ROI 계산 ---

        c = self.config

        roi_w = min(c.roi_width, w)
        roi_h = min(c.roi_height, h)

        cx = w // 2 + c.roi_offset_x
        cy = h // 2 + c.roi_offset_y

        x0 = cx - roi_w // 2
        y0 = cy - roi_h // 2

        # 프레임 경계 안으로 보정
        x0 = max(0, min(cx - roi_w // 2, w - roi_w))
        y0 = max(0, min(cy - roi_h // 2, h - roi_h))

        roi = gray[y0:y0 + roi_h, x0:x0 + roi_w]

        if roi.size == 0:
            return pixel_sum, (x0, y0, roi_w, roi_h), None

        # --- ROI 안에서 가장 밝은 "줄(행)" 찾기 ---
        row_sums = roi.sum(axis=1)  # 각 행의 밝기 총합
        brightest_idx = int(np.argmax(row_sums))  # 0 ~ roi_h-1
        water_y = y0 + brightest_idx             # 프레임 전체 기준 y좌표

        roi_rect = (x0, y0, roi_w, roi_h)
        return pixel_sum, roi_rect, water_y

