# tests/test_controller.py
from app.controller.app_controller import AppController
from app.config import ProtocolConfig


class DummyMotor:
    def __init__(self):
        self.commands = []

    def move_start(self):
        self.commands.append("start")

    def move_stop(self):
        self.commands.append("stop")

    def move_after_low_level(self):
        self.commands.append("move_after_low_level")

class DummyCameraModel:
    def __init__(self):
        self.open_called = False
        self.read_called = 0

    def open(self):
        self.open_called = True

    def read(self):
        self.read_called += 1
        return None  # 실제로는 쓰레드에서만 호출됨

    def release(self):
        pass


class DummyThread:
    def __init__(self, camera_model):
        self.camera_model = camera_model
        self.started = False
        self.stopped = False
        self.wait_called = False
        # frame_ready / finished 시그널이 없으므로 Controller가 getattr로만 접근하도록 설계됨

    def isRunning(self):
        return self.started and not self.stopped

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def wait(self, timeout=None):
        self.wait_called = True


class DummyAnalyzer:
    def __init__(self):
        self.last_frame = None

    def analyze(self, frame):
        self.last_frame = frame
        pixel_sum = 123
        roi_rect = (10, 20, 30, 40)
        water_y = 150  # config 기준으로 1단계 범위 안의 값
        return pixel_sum, roi_rect, water_y


class DummyView:
    def __init__(self):
        self.sum_values = []
        self.video_frames = []
        self.rois = []
        self.water_levels = []
        self.progress_values = []
        self.status_values = []

    def update_sum_label(self, value):
        self.sum_values.append(value)

    def update_video_label(self, frame, roi_rect=None, water_y=None):
        self.video_frames.append(frame)
        self.rois.append(roi_rect)
        self.water_levels.append(water_y)

    def update_progress(self, value):
        self.progress_values.append(value)

    def update_status_label(self, text):
        self.status_values.append(text)

def make_controller_with_dummy(config: ProtocolConfig | None = None):
    camera_model = DummyCameraModel()
    motor = DummyMotor()
    analyzer = DummyAnalyzer()
    cfg = config or ProtocolConfig()

    controller = AppController(
        camera_model=camera_model,
        motor_model=motor,
        analyzer=analyzer,
        camera_thread_cls=DummyThread,
        protocol_config=cfg,
    )
    view = DummyView()
    controller.set_view(view)
    return controller, view, motor



def test_controller_start_stop():
    controller, view, motor = make_controller_with_dummy()

    controller.handle_start()

    # start
    assert motor.commands == ["start"]
    assert isinstance(controller.camera_thread, DummyThread)
    assert controller.camera_thread.started is True

    controller.handle_stop()

    # stop
    assert motor.commands == ["start", "stop"]
    assert controller.camera_thread is None

    # statusLabel 업데이트 여부 검증
    assert view.status_values[-1] == "정지"

def test_controller_on_frame_ready_updates_view():
    controller, view, motor = make_controller_with_dummy()

    fake_frame = "dummy_frame"

    controller.on_frame_ready(fake_frame)

    # Analyzer가 호출되었는지
    assert controller.analyzer.last_frame == fake_frame

    # View 쪽으로 값이 제대로 전달되었는지
    assert view.sum_values == [123]
    assert view.video_frames == [fake_frame]
    assert view.rois == [(10, 20, 30, 40)]
    assert view.water_levels == [150]

    # ProgressBar 값도 1회 업데이트 되었는지
    assert len(view.progress_values) == 1
    progress = view.progress_values[0]
    assert 0 <= progress <= 100

    # waterlevel 자동 로직은 한 번 호출로는 10초가 안 지났으므로
    # 모터의 move_after_low_level은 호출되지 않아야 한다
    assert "move_after_low_level" not in motor.commands