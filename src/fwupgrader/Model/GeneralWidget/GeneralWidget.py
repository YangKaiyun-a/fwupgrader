from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit
)
from PySide6.QtCore import Qt

from src.fwupgrader.Data.DataSet import get_version, ComputerType


def create_version_layout(label_text, line_edit):
    """创建通用布局"""
    label = QLabel(label_text)
    line_edit.setReadOnly(True)
    line_edit.setFixedWidth(350)

    hlayout = QHBoxLayout()
    hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    hlayout.addStretch()
    hlayout.addWidget(label)
    hlayout.addWidget(line_edit)
    hlayout.addStretch()

    return hlayout


class GeneralWidget(QWidget):
    def __init__(self, computer_type):
        super().__init__()
        self.computer_type = computer_type
        self.computer_type_name = None
        self.edit_new_version = None
        self.edit_current_version = None
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        if self.computer_type == ComputerType.Upper:
            self.computer_type_name = '上位机'
        elif self.computer_type == ComputerType.Middle:
            self.computer_type_name = '中位机'

        self.edit_current_version = QLineEdit("Vxx.xx.xx.xxxx")
        self.edit_new_version = QLineEdit("Vxx.xx.xx.xxxx")

        # 主布局
        main_layout = QVBoxLayout(self)

        current_version_hlayout = create_version_layout("当前版本：", self.edit_current_version)
        new_version_hlayout = create_version_layout("最新版本：", self.edit_new_version)

        main_layout.addStretch()
        main_layout.addLayout(current_version_hlayout)
        main_layout.addLayout(new_version_hlayout)
        main_layout.addStretch()

    #每次进入该页面时会调用这个刷新函数
    def refresh_ui(self):
        version = get_version(ComputerType.Upper)
        self.edit_current_version.setText(version)
        print(f"获取到{self.computer_type_name}版本为：{version}")




