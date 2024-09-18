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
from CentralWidget import CentralWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.btnUpper = None
        self.btnMiddel = None
        self.btnLower = None
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        self.setWindowTitle("GP 1.5 软件升级工具")
        self.setGeometry(100, 100, 1920, 1080)

        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)

        self.show()
