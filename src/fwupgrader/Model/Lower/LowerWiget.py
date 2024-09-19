from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)

from src.fwupgrader.Data.DataSet import lower_module_datas
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Model.Lower.controlWidget import UpgradeModule

import os
import canopen
import struct
import re


# 固件升级的主页面
class LowerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.btnImport = None
        self.centerNode = None
        self.ModuleList = None
        self.network = None
        self.init()

    def init(self):
        self.initCanNetwork()
        self.init_ui()
        self.init_connect()

    def initCanNetwork(self):
        # 连接can网络
        self.network = canopen.Network()
        # self.network.connect(channel="can0", bustype="socketcan")

        # 存储此次要升级的固件模块
        self.ModuleList = {}

        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # 创建一个本地节点，节点 ID 为 0x01，并加载 EDS 文件描述节点
        self.centerNode = canopen.LocalNode(0x01, f"{current_dir}/template.eds")
        self.network.add_node(self.centerNode)

        # 设置一个回调函数，在收到 CANopen 网络写入数据时调用
        self.centerNode.add_write_callback(self.on_write)

    # 初始化ui
    def init_ui(self):
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)

        contentWidget = QWidget()
        contenLayout = QGridLayout(contentWidget)
        scrollArea.setWidget(contentWidget)

        topWidget = QWidget()
        topLayout = QHBoxLayout(topWidget)
        self.btnImport = QPushButton("导入更新文件")
        self.btnImport.setFixedSize(150, 50)
        self.btnImport.clicked.connect(self.onBtnImportClicked)

        topLayout.addWidget(self.btnImport)

        for idx, data in enumerate(lower_module_datas):
            # 创建每个固件，并根据cob_id存储在ModuleList容器中
            update = UpgradeModule(data[0], data[1], data[2], self.network, self)
            self.ModuleList[data[0]] = update

            # 将固件添加入布局中
            contenLayout.addWidget(
                update,
                idx // 4,
                idx % 4,
            )

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(topWidget)
        mainLayout.addWidget(scrollArea)

        self.setLayout(mainLayout)

    def init_connect(self):
        signal_manager.sigUpdateLowerAdress.connect(self.onSigUpdateLowerAdress)

    def onBtnImportClicked(self):
        fd = QtWidgets.QFileDialog()
        fd.setFileMode(QtWidgets.QFileDialog.Directory)
        fd.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        if fd.exec():
            f = fd.selectedFiles()
            path = f[0]
            # 获取指定目录 path 下的所有文件和子目录的名称列表
            files = os.listdir(path)
            # 过滤出所有以 .bin 结尾的文件
            bins = [file for file in files if file.endswith(".bin")]
            print(bins)

            for binFile in bins:
                # 在 datas 列表中查找与前缀匹配的设备
                prefix = binFile.split(".")[0]
                item = [data for data in lower_module_datas if data[2] == prefix]

                if len(item) == 0:
                    continue

                cid, _, _ = item[0]

                # 更新每个固件的地址
                self.ModuleList[cid].on_file_update(os.path.join(path, binFile))

    # 从文件名 amplification_cool.V01.03.01.1001.bin 中解析出版本号 V01.03.01.1001
    def get_version_from_file(self, file_name):
        version_string = ""
        match = re.search(r'V\d+\.\d+\.\d+\.\d+', file_name)
        if match:
            version_string = match.group(0)

        return version_string

    def onSigUpdateLowerAdress(self, bin_file_dict):
        for file_name, file_path in bin_file_dict.items():

            prefix = file_name.split(".")[0]
            new_version = self.get_version_from_file(file_name)
            item = [data for data in lower_module_datas if data[2] == prefix]

            if len(item) == 0:
                continue

            cid, _, _ = item[0]

            # 更新每个固件的地址
            self.ModuleList[cid].on_file_update(file_path, new_version)

    def on_write(self, index, subindex, od, data):
        # 解包收到的二进制数据，将其解析为两个 16 位无符号整数，分别为 value 和 cob_id
        value, cob_id = struct.unpack("HH", data)

        print(f"codid {cob_id} index {hex(index)} subindex{hex(subindex)} value {value}")

        for _, w in self.ModuleList.items():
            if w.in_process:
                w.receive_module_reply(index, subindex, value)
                break
