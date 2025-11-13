# app/services/video_analyzer.py
import numpy as np
import cv2


class VideoAnalyzer:
    """
    영상 분석을 담당하는 별도 모듈.
    여기서 ROI 분석, threshold, 수면 레벨 등 다 확장 가능.
    지금은 '픽셀 총합'만 계산.
    """

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
