from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QProgressBar,
    QVBoxLayout,
    QDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, QThread, Slot, Signal


class MiddelWiget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        pass