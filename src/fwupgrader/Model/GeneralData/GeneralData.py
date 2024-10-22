from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QObject
from src.fwupgrader.Data.DataSet import (
    get_current_version_from_file,
    get_new_version_from_file
)
from src.fwupgrader.Data.Global import ComputerType


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


class GeneralData(QObject):
    def __init__(self, computer_type):
        super().__init__()
        self.computer_type = computer_type  # 区分上位机、中位机、QPCR
        self.computer_type_name = None      # 字符串，"上位机"、"中位机"、"QPCR"
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
        elif self.computer_type == ComputerType.QPCR:
            self.computer_type_name = 'QPCR'

        self.init_file_info()

    def init_file_info(self):
        """初始化所有信息"""
        self.fw = None
        self.new_version = "Vxx.xx.xx.xxxx"
        self.is_update = False
        self.get_current_version_from_file()

    def get_current_version_from_file(self):
        """从文件中获取当前版本号"""
        version = get_current_version_from_file(ComputerType.Upper)
        self.current_version = version
        print(f"获取到{self.computer_type_name}当前版本为：{version}")

    def update_file_info(self, file_absolute_path):
        """更新升级路径"""
        self.init_file_info()
        self.fw = file_absolute_path
        new_version = get_new_version_from_file(file_absolute_path)
        self.new_version = new_version
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    def get_fw(self):
        """返回升级路径"""
        return self.fw

    def set_is_update(self, is_update):
        self.is_update = is_update

    def get_computer_type(self):
        """返回区分上位机、中位机、QPCR"""
        return self.computer_type

    def get_computer_type_name(self):
        """返回上位机、中位机、QPCR的字符串"""
        return self.computer_type_name

    def get_new_version(self):
        """返回最新版本"""
        return self.new_version

    def get_current_version(self):
        """返回当前版本"""
        return self.current_version
