# app/config.py
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class ProtocolConfig:
    # 프로그레스바용
    step1_min: int = 100   # 1단계 시작 waterlevel
    step1_max: int = 200   # 1단계 끝   waterlevel
    step2_min: int = 100   # 2단계 시작 waterlevel
    step2_max: int = 200   # 2단계 끝   waterlevel

    # 자동 동작용
    move_threshold: int = 200      # 10초 동안 이 값 이하 → 모터 이동
    move_duration_sec: float = 10  # 위 조건 유지 시간 (초)

    stop_threshold: int = 300      # 10초 동안 이 값 이하 → Stop
    stop_duration_sec: float = 10  # 위 조건 유지 시간 (초)

    # ROI 설정 추가
    roi_width: int = 100
    roi_height: int = 100
    roi_offset_x: int = 0
    roi_offset_y: int = 0

    @classmethod
    def from_json(cls, path: Path):


        if not path.exists():
            # 파일 없으면 기본값 사용
            return cls()

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
