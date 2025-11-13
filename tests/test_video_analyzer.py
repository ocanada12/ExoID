# tests/test_video_analyzer.py
import numpy as np
from app.services.video_analyzer import VideoAnalyzer


def test_calculate_sum_gray():
    analyzer = VideoAnalyzer()
    frame = np.ones((10, 10), dtype=np.uint8) * 10
    result = analyzer.calculate_sum(frame)
    assert result == 10 * 100  # 10x10 픽셀, 값 10


def test_calculate_sum_color():
    analyzer = VideoAnalyzer()
    # BGR 이미지 (모두 100,100,100)
    frame = np.ones((5, 5, 3), dtype=np.uint8) * 100
    result = analyzer.calculate_sum(frame)
    # gray 변환 후 총합이 양수인지 정도만 체크
    assert result > 0


def test_calculate_sum_none():
    analyzer = VideoAnalyzer()
    result = analyzer.calculate_sum(None)
    assert result == 0
