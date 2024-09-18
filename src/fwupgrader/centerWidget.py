from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QMenuBar,
    QMenu,
    QGridLayout
)


from controlWidget import UpgradeWidget
from PySide6.QtCore import Slot
import os
import canopen
import struct

# cob_id, 名称， 前缀
datas = [
    (0x09, "扩增冷存", "amplification_cool"),
    (0x07, "扩增DJ1", "amplification_dj1"),
    (0x2E, "扩增DJ1电容", "dj_capacitance_1"),
    (0x05, "提取DJ2", "extract_dj1"),
    (0x2F, "扩增DJ1电容", "dj_capacitance_2"),
    (0x24, "DP1夹爪", "dp1_jaw"),
    (0x23, "DP1龙门架", "dp1_xy"),
    (0x04, "DP8移液器", "dp8"),
    (0x2D, "DP8气压电容检测", "pressure_capacitance"),
    (0x03, "DP8龙门架", "dp8_xy"),
    (0x06, "热封模块", "heat_seal"),
    (0x26, "加热振荡1", "heat_shake_1"),
    (0x27, "加热振荡2", "heat_shake_2"),
    (0x28, "加热振荡3", "heat_shake_3"),
    (0x29, "加热振荡4", "heat_shake_4"),
    (0x2A, "加热振荡5", "heat_shake_5"),
    (0x2B, "磁珠振荡", "heat_shake_6"),
    (0x0A, "开关信号", "switch_signal"),
    (0x0B, "紫外状态灯", "light_status"),
    (0x08, "核酸冷存", "cool_store"),
    (0x0C, "风道气压", "environment_monitor"),
    (0x22, "转运", "transporter"),
    (0x0E, "Q龙门架夹爪", "xz_claw"),
]


class CenterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 连接can网络
        self.network = canopen.Network()
        # self.network.connect(channel="can0", bustype="socketcan")

        # 存储UpgradeWidget类
        self.controlWidgets = {}

        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # 创建一个本地节点，节点 ID 为 0x01，并加载 EDS 文件描述节点
        self.centerNode = canopen.LocalNode(0x01, f"{current_dir}/template.eds")
        self.network.add_node(self.centerNode)

        # 设置一个回调函数，在收到 CANopen 网络写入数据时调用
        self.centerNode.add_write_callback(self.on_write)

        self.initUI()

    def on_write(self, index, subindex, od, data):
        # 解包收到的二进制数据，将其解析为两个 16 位无符号整数，分别为 value 和 cob_id
        value, cob_id = struct.unpack("HH", data)

        print(
            f"codid {cob_id} index {hex(index)} subindex{hex(subindex)} value {value}"
        )

        for _, w in self.controlWidgets.items():
            if w.in_process:
                w.on_reply(index, subindex, value)
                break

        """
        w = self.controlWidgets.get(cob_id)
        if w:
            w.on_reply(index, subindex, value)
        """


    def initUI(self):
        mainlayout = QGridLayout()

        for idx, data in enumerate(datas):
            # 创建每个固件，并根据cob_id存储在controlWidgets容器中
            update = UpgradeWidget(data[0], data[1], data[2], self.network, self)
            self.controlWidgets[data[0]] = update

            # 将固件添加入布局中
            mainlayout.addWidget(
                update,
                idx // 4,
                idx % 4,
            )

        self.setLayout(mainlayout)

    # 用于标记该函数为槽函数，参数类型为str，接收固件文件路径
    @Slot(str)
    def on_path_update(self, path):
        # 获取指定目录 path 下的所有文件和子目录的名称列表
        files = os.listdir(path)
        # 过滤出所有以 .bin 结尾的文件
        bins = [file for file in files if file.endswith(".bin")]

        for binFile in bins:
            # 在 datas 列表中查找与前缀匹配的设备
            prefix = binFile.split(".")[0]
            item = [data for data in datas if data[2] == prefix]

            if len(item) == 0:
                continue

            cid, _, _ = item[0]

            # 更新每个固件的地址
            self.controlWidgets[cid].on_file_update(os.path.join(path, binFile))
