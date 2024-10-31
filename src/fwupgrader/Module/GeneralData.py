from PySide6.QtCore import QObject
from src.fwupgrader.Data.DataSet import (
    get_current_version_from_file,
    get_new_version_from_file
)
from src.fwupgrader.Data.Global import ComponentType, ComponentType_name_map


class GeneralData(QObject):
    def __init__(self, component_type):
        super().__init__()
        self.component_type = component_type    # 区分上位机、中位机、QPCR、固件
        self.component_type_name = None         # 字符串，"上位机"、"中位机"、"QPCR"
        self.new_version = None                 # 最新版本
        self.current_version = None             # 当前版本
        self.fw = None                          # 升级文件路径
        self.in_process = False                 # 是否在升级过程中
        self.status = "--"                      # 状态
        self.init()

    def init(self):
        self.init_data()

    def init_data(self):
        """初始化数据"""
        self.component_type_name = ComponentType_name_map.get(self.component_type)
        self.init_file_info()

    def init_file_info(self):
        """初始化所有信息"""
        self.fw = None
        self.new_version = ""
        self.in_process = False
        self.get_current_version_from_file()

    def get_current_version_from_file(self):
        """从文件中获取当前版本号"""
        self.current_version = get_current_version_from_file(self.component_type)
        print(f"获取到{self.component_type_name}当前版本为：{self.current_version}")

    def update_file_info(self, file_absolute_path):
        """更新升级路径"""
        self.fw = file_absolute_path
        self.new_version = get_new_version_from_file(self.component_type, file_absolute_path)
        print(f"获取到{self.component_type_name}最新版本为：{self.new_version}")

        if self.current_version == "获取失败":
            self.status = "不可升级"
        else:
            if self.new_version != self.current_version:
                self.status = "可升级"
            else:
                self.status = "无需升级"

    def get_fw(self):
        """返回升级路径"""
        return self.fw

    def set_in_process(self, in_process):
        self.in_process = in_process

    def get_component_type(self):
        """返回区分上位机、中位机、QPCR"""
        return self.component_type

    def get_component_type_name(self):
        """返回上位机、中位机、QPCR的字符串"""
        return self.component_type_name

    def get_new_version(self):
        """返回最新版本"""
        return self.new_version

    def get_current_version(self):
        """返回当前版本"""
        # self.get_current_version_from_file()
        return self.current_version

    def get_status(self):
        """返回状态"""
        return self.status

    def set_status(self, new_status):
        """设置状态"""
        self.status = new_status