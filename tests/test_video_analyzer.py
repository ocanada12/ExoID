# tests/test_video_analyzer.py
import numpy as np
from app.services.video_analyzer import VideoAnalyzer
from app.config import ProtocolConfig


def test_calculate_sum_gray():
    analyzer = VideoAnalyzer(ProtocolConfig())
    frame = np.ones((10, 10), dtype=np.uint8) * 10
    result = analyzer.calculate_sum(frame)
    assert result == 10 * 100  # 10x10 픽셀, 값 10


def test_calculate_sum_color():
    analyzer = VideoAnalyzer(ProtocolConfig())
    # BGR 이미지 (모두 100,100,100)
    frame = np.ones((5, 5, 3), dtype=np.uint8) * 100
    result = analyzer.calculate_sum(frame)
    # gray 변환 후 총합이 양수인지 정도만 체크
    assert result > 0


def test_calculate_sum_none():
    analyzer = VideoAnalyzer(ProtocolConfig())
    result = analyzer.calculate_sum(None)
    assert result == 0


def test_analyze_returns_roi_and_waterlevel():
    analyzer = VideoAnalyzer(ProtocolConfig())

    # 200x200 BGR 이미지, 전부 10으로 채우고
    frame = np.ones((200, 200, 3), dtype=np.uint8) * 10

    # 중앙 ROI 안의 특정 줄만 더 밝게
    # 중앙 ROI는 대략 (50~149, 50~149) 근처라 가정
    # ROI 중앙 줄을 200으로 올려보자
    h, w = frame.shape[:2]
    center_y = h // 2
    frame[center_y, :, :] = 200  # 가운데 한 줄을 밝게

    pixel_sum, roi_rect, water_y = analyzer.analyze(frame)

    assert pixel_sum > 0
    assert roi_rect is not None
    x, y, rw, rh = roi_rect
    # water_y는 ROI 영역 안이어야 함
    assert y <= water_y < y + rh