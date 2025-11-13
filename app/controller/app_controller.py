# app/controller/app_controller.py
from PyQt5.QtCore import QObject
from app.threads.camera_thread import CameraThread
from app.services.video_analyzer import VideoAnalyzer


class AppController(QObject):
    """
    MVC에서 Controller 역할.
    - View의 버튼 이벤트를 처리
    - CameraThread, MotorModel, VideoAnalyzer를 연결
    """

    def __init__(self, camera_model, motor_model, analyzer=None, camera_thread_cls=CameraThread, parent=None):
        super().__init__(parent)
        self.camera_model = camera_model
        self.motor_model = motor_model
        self.analyzer = analyzer or VideoAnalyzer()
        self.camera_thread_cls = camera_thread_cls

        self.view = None
        self.camera_thread = None

    def set_view(self, view):
        self.view = view

    # --- UI 이벤트 핸들러 ---

    def handle_start(self):
        """Start 버튼 눌렀을 때: 스트리밍 시작 + 모터 이동."""
        if self.camera_thread and getattr(self.camera_thread, "isRunning", lambda: False)():
            # 이미 실행 중이면 무시
            return

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

    # --- CameraThread → Controller ---

    def on_frame_ready(self, frame):
        """카메라 쓰레드에서 프레임이 들어왔을 때."""
        if self.view is None:
            return

        pixel_sum = self.analyzer.calculate_sum(frame)
        self.view.update_sum_label(pixel_sum)
        self.view.update_video_label(frame)

    def on_camera_finished(self):
        """카메라 쓰레드 종료 후 호출."""
        self.camera_thread = None
