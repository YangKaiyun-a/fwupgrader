from PySide6.QtWidgets import (
    QWidget,
)

from PySide6.QtCore import Signal
import canopen
import os


from src.fwupgrader.Data.Global import ComponentType
from src.fwupgrader.Data.SignalManager import signal_manager

class LowerData(QWidget):
    sig = Signal(bool)

    def __init__(self, cob_id, name, network):
        super().__init__()
        self.component_type = ComponentType.Lower   # 区分上位机、中位机、QPCR、固件
        self.component_type_name = name             # 设备名称
        self.current_version = None                 # 当前版本
        self.new_version = None                     # 最新版本
        self.cob_id = cob_id                        # 设备ID，hex(self.cob_id)
        self.fw = None                              # 固件文件路径
        self.in_process = False                     # 是否在升级中
        self.network = network                      # CAN网络
        self.remote = None                          # 远程节点
        self.status = "--"                          # 状态
        self.init()

    def init(self):
        self.init_data()

    def init_data(self):
        """初始化数据"""
        self.init_file_info()

        # 添加远程节点到CANopen网络
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.remote = canopen.RemoteNode(self.cob_id, f"{current_dir}/template.eds")
        self.network.add_node(self.remote)

    def init_file_info(self):
        """初始化所有信息"""
        self.fw = None
        self.new_version = ""
        self.in_process = False
        self.get_current_version_from_file()

    def get_current_version_from_file(self):
        """从文件中获取当前版本号"""
        ver = "获取失败"

        try:
            num = self.remote.sdo["module_version"]["version_num"].raw
            ver = f"{num >> 24}.{(num >> 16) & 0xFF}.{(num >> 8) & 0xFF}.{num & 0xFF}"
        except Exception as e:
            print(e)

        self.current_version = ver

    def receive_module_reply(self, cob_id):
        """固件回复后调用这个函数，发出信号释放线程信号量"""
        if cob_id != self.cob_id:
            return

        signal_manager.sigModuleReply.emit(cob_id, True)

    def update_file_info(self, path, new_version):
        """更新升级路径"""
        self.clear_file_info()
        self.fw = path
        self.new_version = new_version
        print(f"更新的模块名称：{self.component_type_name}，版本号为：{self.new_version}，路径为：{self.fw}")

        if self.current_version == "获取失败":
            self.status = "不可升级"
        else:
            if self.new_version != self.current_version:
                self.status = "可升级"
            else:
                self.status = "无需升级"

    def clear_file_info(self):
        self.fw = None
        self.new_version = "Vxx.xx.xx.xxxx"

    def get_component_type(self):
        """获取区分上位机、中位机、QPCR"""
        return self.component_type

    def get_component_type_name(self):
        """获取固件名称"""
        return self.component_type_name

    def get_current_version(self):
        """获取当前固件版本号"""
        return self.current_version

    def get_new_version(self):
        """获取最新固件版本号"""
        return self.new_version

    def get_remote(self):
        """远程节点"""
        return self.remote

    def get_fw(self):
        """获取升级路径"""
        return self.fw

    def set_in_process(self, in_process):
        self.in_process = in_process

    def get_in_process(self, in_process):
        return self.in_process

    def get_status(self):
        """获取升级状态"""
        return self.status

    def set_status(self, new_status):
        """设置状态"""
        self.status = new_status

    def get_cob_id(self):
        """返回设备ID"""
        return self.cob_id