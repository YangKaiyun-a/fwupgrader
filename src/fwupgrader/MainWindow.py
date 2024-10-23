from PySide6 import QtWidgets
from CentralWidget import CentralWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        self.setWindowTitle("GP 1.5 软件升级工具")
        self.setGeometry(100, 100, 1394, 752)

        central_widget = CentralWidget()
        self.setCentralWidget(central_widget)

        self.show()