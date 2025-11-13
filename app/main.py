# app/main.py
import sys
from PyQt5.QtWidgets import QApplication
from app.model.camera_model import CameraModel
from app.model.motor_model import MotorModel
from app.controller.app_controller import AppController
from app.view.main_view import MainWindow


def main():
    app = QApplication(sys.argv)

    camera_model = CameraModel(index=0)
    motor_model = MotorModel()
    controller = AppController(camera_model=camera_model, motor_model=motor_model)

    window = MainWindow(controller=controller)
    controller.set_view(window)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
