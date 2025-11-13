# tests/test_motor_model.py
from app.model.motor_model import MotorModel


def test_motor_model_commands():
    motor = MotorModel()
    assert motor.last_command is None

    motor.move_start()
    assert motor.last_command == "start"

    motor.move_stop()
    assert motor.last_command == "stop"
