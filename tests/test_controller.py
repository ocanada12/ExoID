# tests/test_controller.py
from app.controller.app_controller import AppController


class DummyMotor:
    def __init__(self):
        self.commands = []

    def move_start(self):
        self.commands.append("start")

    def move_stop(self):
        self.commands.append("stop")


class DummyCameraModel:
    def __init__(self):
        self.open_called = False

    def open(self):
        self.open_called = True

    def read(self):
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

    def calculate_sum(self, frame):
        self.last_frame = frame
        return 123  # 고정된 값 리턴


class DummyView:
    def __init__(self):
        self.sum_values = []
        self.video_frames = []

    def update_sum_label(self, value):
        self.sum_values.append(value)

    def update_video_label(self, frame):
        self.video_frames.append(frame)


def test_controller_start_stop():
    camera_model = DummyCameraModel()
    motor = DummyMotor()
    analyzer = DummyAnalyzer()

    controller = AppController(
        camera_model=camera_model,
        motor_model=motor,
        analyzer=analyzer,
        camera_thread_cls=DummyThread,
    )

    view = DummyView()
    controller.set_view(view)

    # start
    controller.handle_start()
    assert motor.commands == ["start"]
    assert isinstance(controller.camera_thread, DummyThread)
    assert controller.camera_thread.started is True

    # stop
    controller.handle_stop()
    assert motor.commands == ["start", "stop"]
    assert controller.camera_thread is None


def test_controller_on_frame_ready_updates_view():
    camera_model = DummyCameraModel()
    motor = DummyMotor()
    analyzer = DummyAnalyzer()
    controller = AppController(
        camera_model=camera_model,
        motor_model=motor,
        analyzer=analyzer,
        camera_thread_cls=DummyThread,
    )
    view = DummyView()
    controller.set_view(view)

    fake_frame = "dummy_frame"
    controller.on_frame_ready(fake_frame)

    assert analyzer.last_frame == fake_frame
    assert view.sum_values == [123]
    assert view.video_frames == [fake_frame]
