from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit
)
from PySide6.QtCore import Qt

from src.fwupgrader.Data.DataSet import get_version, ComputerType, get_version_from_file
from src.fwupgrader.Data.SignalManager import signal_manager


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
        self.computer_type = computer_type      # 区分上位机、中位机
        self.computer_type_name = None          # 字符串，"上位机"或"中位机"
        self.edit_new_version = None            # 最新版本QLinEdit
        self.edit_current_version = None        # 当前版本QLineEdit
        self.fw = None                          # 升级文件路径
        self.init()

    def init(self):
        self.init_ui()
        self.init_connect()

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
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        current_version_hlayout = create_version_layout("当前版本：", self.edit_current_version)
        new_version_hlayout = create_version_layout("最新版本：", self.edit_new_version)
        push_button_hlayout = QHBoxLayout()

        btn_update = QPushButton("升级")
        btn_update.setFixedSize(135, 45)
        btn_update.clicked.connect(self.onBtnUpdateClicked)
        push_button_hlayout.addWidget(btn_update)

        main_layout.addStretch()
        main_layout.addLayout(current_version_hlayout)
        main_layout.addLayout(new_version_hlayout)
        main_layout.addLayout(push_button_hlayout)
        main_layout.addStretch()

    def init_connect(self):
        signal_manager.sigUpdateUpperAddress.connect(self.onSigUpdateUpperAddress)
        signal_manager.sigUpdateMiddleAddress.connect(self.onSigUpdateMiddleAddress)

    def onSigUpdateUpperAddress(self, file_absolute_path):
        if self.computer_type == ComputerType.Middle:
            return

        self.clear_file_info()
        self.fw = file_absolute_path
        new_version = get_version_from_file(file_absolute_path)
        self.edit_new_version.setText(new_version)
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    def onSigUpdateMiddleAddress(self, file_absolute_path):
        if self.computer_type == ComputerType.Upper:
            return

        self.clear_file_info()
        self.fw = file_absolute_path
        new_version = get_version_from_file(file_absolute_path)
        self.edit_new_version.setText(new_version)
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    #每次进入该页面时会调用这个刷新函数
    def refresh_ui(self):
        version = get_version(ComputerType.Upper)
        self.edit_current_version.setText(version)
        print(f"获取到{self.computer_type_name}当前版本为：{version}")

    def clear_file_info(self):
        self.fw = None
        self.edit_new_version.setText("Vxx.xx.xx.xxxx")


    def onBtnUpdateClicked(self):
        pass

