# app/controller/app_controller.py
import time
from PyQt5.QtCore import QObject
from app.threads.camera_thread import CameraThread
from app.services.video_analyzer import VideoAnalyzer
from app.config import ProtocolConfig


class AppController(QObject):
    """
    MVC에서 Controller 역할.
    - View의 버튼 이벤트를 처리
    - CameraThread, MotorModel, VideoAnalyzer를 연결
    """

    def __init__(        self,
        camera_model,
        motor_model,
        analyzer=None,
        camera_thread_cls=CameraThread,
        protocol_config: ProtocolConfig | None = None,
        parent=None,
                         ):
        super().__init__(parent)
        self.camera_model = camera_model
        self.motor_model = motor_model
        self.analyzer = analyzer or VideoAnalyzer()
        self.camera_thread_cls = camera_thread_cls

        self.config = protocol_config or ProtocolConfig()

        self.view = None
        self.camera_thread = None

        # waterlevel 기반 자동 제어 상태
        self._phase = 0  # 0: 아직 아무것도 안함 / 1: 1단계 끝, 2단계 대기 / 2: 모두 완료
        self._phase1_start_time = None  # waterlevel <= 200 유지 시작 시각
        self._phase2_start_time = None  # waterlevel <= 300 유지 시작 시각

    def _reset_waterlevel_logic(self):
        self._phase = 0
        self._phase1_start_time = None
        self._phase2_start_time = None

    def set_view(self, view):
        self.view = view

    # --- UI 이벤트 핸들러 ---

    def handle_start(self):
        """Start 버튼 눌렀을 때: 스트리밍 시작 + 모터 이동."""
        if self.camera_thread and getattr(self.camera_thread, "isRunning", lambda: False)():
            # 이미 실행 중이면 무시
            return

        self._reset_waterlevel_logic()

        self.motor_model.move_start()

        self.camera_thread = self.camera_thread_cls(self.camera_model)
        # CameraThread가 QThread일 수도, 더미 클래스일 수도 있어서 getattr 사용
        if hasattr(self.camera_thread, "frame_ready"):
            self.camera_thread.frame_ready.connect(self.on_frame_ready)

        if hasattr(self.camera_thread, "finished"):
            self.camera_thread.finished.connect(self.on_camera_finished)

        if hasattr(self.camera_thread, "start"):
            self.camera_thread.start()

    def handle_stop(self):
        """Stop 버튼 눌렀을 때: 스트리밍 종료 + 모터 이동."""
        self.motor_model.move_stop()

        if self.camera_thread:
            if hasattr(self.camera_thread, "stop"):
                self.camera_thread.stop()
            if hasattr(self.camera_thread, "wait"):
                self.camera_thread.wait()
            self.camera_thread = None

        self._reset_waterlevel_logic()

    # --- CameraThread → Controller ---

    def on_frame_ready(self, frame):
        """카메라 쓰레드에서 프레임이 들어왔을 때."""
        if self.view is None:
            return

        # 새 분석 함수 사용 (ROI + 수면 레벨)
        if hasattr(self.analyzer, "analyze"):
            pixel_sum, roi_rect, water_y = self.analyzer.analyze(frame)
        else:
            # 옛 analyze 미구현 Analyzer를 위한 fallback
            pixel_sum = self.analyzer.calculate_sum(frame)
            roi_rect, water_y = None, None

        progress = self.calculate_progress(water_y)
        self.view.update_progress(progress)

        self.view.update_sum_label(water_y)
        self.view.update_video_label(frame, roi_rect, water_y)
        self._update_waterlevel_logic(water_y)

    def on_camera_finished(self):
        """카메라 쓰레드 종료 후 호출."""
        self.camera_thread = None


    def _update_waterlevel_logic(self, water_y):
        """
        water_y: VideoAnalyzer.analyze()에서 넘어온 수면 레벨 (y 좌표 또는 수치)
        요구사항:
        1) water_y가 10초 동안 200 이하로 유지 → 모터 이동
        2) 그 이후에 다시 10초 동안 300 이하로 유지 → Stop 버튼 실행(handle_stop)
        """
        # water_y가 계산 안 된 경우 (None)면 타이머 초기화만 하고 리턴
        now = time.time()
        c = self.config

        # 1단계: water_y <= 200이 10초 동안 유지되면 모터 이동
        if self._phase == 0:
            if water_y is not None and water_y <= c.move_threshold:
                if self._phase1_start_time is None:
                    self._phase1_start_time = now
                else:
                    elapsed = now - self._phase1_start_time
                    print(elapsed)
                    if elapsed >= c.move_duration_sec:
                        # 1단계 동작 실행: 모터 이동
                        self.motor_model.move_after_low_level()
                        # 다음 단계로 전환
                        self._phase = 1
                        self._phase2_start_time = None
            else:
                # 조건 깨지면 타이머 리셋
                self._phase1_start_time = None
                print("1단계 : 처음부터 다시")

        # 2단계: water_y <= 300이 10초 동안 유지되면 Stop 실행
        elif self._phase == 1:
            if water_y is not None and water_y <= c.stop_threshold:
                if self._phase2_start_time is None:
                    self._phase2_start_time = now
                else:
                    elapsed = now - self._phase2_start_time
                    print(elapsed)
                    if elapsed >= c.stop_duration_sec:
                        # Stop 버튼과 같은 동작 수행
                        self.handle_stop()
                        # 완전히 종료 상태
                        self._phase = 2
            else:
                # 조건 깨지면 타이머 리셋
                self._phase2_start_time = None
                print("2단계 : 처음부터 다시")
        # _phase == 2 인 경우는 이미 Stop까지 끝난 상태라 추가 처리 없음

    def calculate_progress(self, water_y):
        if water_y is None:
            return 0

        wl = water_y
        c = self.config

        # Phase 0 → 1단계
        if self._phase == 0:
            if wl <= c.step1_min:
                return 0
            if wl >= c.step1_max:
                return 50
            ratio = (wl - c.step1_min) / (c.step1_max - c.step1_min)
            return ratio * 50

        # Phase 1 → 2단계: (step2_min ~ step2_max) → 50~100%
        if self._phase == 1:
            if wl <= c.step2_min:
                return 50
            if wl >= c.step2_max:
                return 100
            ratio = (wl - c.step2_min) / (c.step2_max - c.step2_min)
            return 50 + ratio * 50

        # Phase 2 이후는 다 끝난 상태라 100%로 고정
        return 100