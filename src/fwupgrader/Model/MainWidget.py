from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Slot, Signal

class MainWidget(QWidget):
    # 定义信号，传递按钮标识符
    sigButtonClicked = Signal(int)


    def __init__(self):
        super().__init__()
        self.btnUpper = None
        self.btnMiddel = None
        self.btnLower = None
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        self.btnUpper = QPushButton("上位机升级")
        self.btnUpper.setFixedSize(200, 50)

        self.btnMiddel = QPushButton("中位机升级")
        self.btnMiddel.setFixedSize(200, 50)
        self.btnLower = QPushButton("固件升级")
        self.btnLower.setFixedSize(200, 50)

        self.btnUpper.clicked.connect(self.onBtnUpperClicked)
        self.btnMiddel.clicked.connect(self.onBtnMiddelClicked)
        self.btnLower.clicked.connect(self.onBtnLowerClicked)

        # 布局
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(9)
        mainLayout.addWidget(self.btnUpper)
        mainLayout.addWidget(self.btnMiddel)
        mainLayout.addWidget(self.btnLower)
        self.setLayout(mainLayout)


    def onBtnUpperClicked(self):
        self.sigButtonClicked.emit(1)

    def onBtnMiddelClicked(self):
        self.sigButtonClicked.emit(2)

    def onBtnLowerClicked(self):
        self.sigButtonClicked.emit(3)
