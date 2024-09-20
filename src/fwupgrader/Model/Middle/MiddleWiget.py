from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLineEdit
)
from PySide6.QtCore import Qt
from src.fwupgrader.Data.DataSet import get_version, ComputerType

class MiddleWiget(QWidget):
    def __init__(self):
        super().__init__()
        self.edit_current_version = None
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)

        lab_current_version = QLabel("当前版本：")
        self.edit_current_version = QLineEdit()
        self.edit_current_version.setReadOnly(True)
        self.edit_current_version.setFixedWidth(350)
        self.edit_current_version.setText("Vxx.xx.xx.xxxx")

        version_hlayout = QHBoxLayout()
        version_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_hlayout.addStretch()

        version_hlayout.addWidget(lab_current_version)
        version_hlayout.addWidget(self.edit_current_version)

        version_hlayout.addStretch()
        main_layout.addLayout(version_hlayout)

    def refresh_ui(self):
        version = get_version(ComputerType.Middle)
        self.edit_current_version.setText(version)
        print(f"获取到上位机版本为：{version}")