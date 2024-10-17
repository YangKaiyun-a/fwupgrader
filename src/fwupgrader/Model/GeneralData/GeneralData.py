from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout
)
from PySide6.QtCore import Qt, Slot, QThread, QObject
from src.fwupgrader.Data.DataSet import (
    get_version,
    ComputerType,
    get_version_from_file,
    execute_upgrade_script,
    ResultType
)
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


class UpgradeThread(QThread):
    def __init__(self, fw, computer_type, parent=None):
        super().__init__(parent)
        self.fw = fw
        self.computer_type = computer_type

    def run(self):
        execute_upgrade_script(self.fw, self.computer_type)


class GeneralData(QObject):
    def __init__(self, computer_type):
        super().__init__()
        self.computer_type = computer_type  # 区分上位机、中位机
        self.computer_type_name = None      # 字符串，"上位机"或"中位机"
        self.new_version = None             # 最新版本
        self.current_version = None         # 当前版本
        self.fw = None                      # 升级文件路径
        self.is_update = False              # 是否在升级过程中
        self.init()

    def init(self):
        self.init_data()

    def init_data(self):
        """初始化数据"""
        if self.computer_type == ComputerType.Upper:
            self.computer_type_name = '上位机'
        elif self.computer_type == ComputerType.Middle:
            self.computer_type_name = '中位机'

        self.new_version = "Vxx.xx.xx.xxxx"
        self.current_version = "Vxx.xx.xx.xxxx"

    def get_current_version(self):
        """获取当前版本号"""
        version = get_version(ComputerType.Upper)
        self.current_version = version
        print(f"获取到{self.computer_type_name}当前版本为：{version}")

    def clear_file_info(self):
        """清空所有信息"""
        self.fw = None
        self.new_version = "Vxx.xx.xx.xxxx"
        self.is_update = False

    def update_machine(self):
        """执行升级"""
        if not self.fw:
            return ResultType.Empty_File_path

        self.is_update = True
        # 执行升级
        upgrade_thread = UpgradeThread(self.fw, self.computer_type)
        upgrade_thread.start()

        return ResultType.Start_Update

    def update_file_info(self, file_absolute_path):
        """更新升级路径"""
        self.clear_file_info()
        self.fw = file_absolute_path
        new_version = get_version_from_file(file_absolute_path)
        self.new_version = new_version
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    def handle_execute_script_result(self, message):
        """升级结果"""

        # 通过是否处于升级状态来区分上、中位机
        if not self.is_update:
            return

        self.is_update = False

        # self.result_dlg.setText(message)
        # self.result_dlg.setBtnEnabled(True)

        self.clear_file_info()
        self.get_current_version()
