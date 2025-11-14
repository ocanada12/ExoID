# app/model/motor_model.py

class MotorModel:
    """
    모터를 제어하는 Model.
    실제로는 시리얼 통신 등의 코드를 넣으면 되고,
    지금은 테스트 가능하도록 상태만 기록.
    """

    def __init__(self):
        self.last_command = None

    def move_start(self):
        # TODO: 실제 모터 이동 코드 (예: 시리얼로 "START" 전송)
        self.last_command = "start"

    def move_stop(self):
        # TODO: 실제 모터 정지 코드
        self.last_command = "stop"

    def move_after_low_level(self):
        """
        waterlevel이 10초 동안 200 이하일 때 실행할 모터 동작.
        여기에 실제 '이동' 동작(예: 특정 위치로 이동)을 넣으면 됨.
        """
        # TODO: 실제 모터 이동 코드 (예: "MOVE_STAGE1" 같은 명령)
        self.last_command = "move_after_low_level"