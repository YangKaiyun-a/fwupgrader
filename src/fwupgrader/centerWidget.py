from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
)
from PySide6.QtWidgets import QMenuBar, QMenu, QGridLayout

from controlWidget import upgradeWidget
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
    # 哪个是哪个
    (0x0E, "Q龙门架夹爪", "xz_claw"),
]


class centerWidget(QWidget):
    def __init__(self, parent=None):
        super(centerWidget, self).__init__(parent)

        self.network = canopen.Network()
        # self.network.connect(channel="can0", bustype="socketcan")

        self.controlWidgets = {}
        self.initUI()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.centerNode = canopen.LocalNode(0x01, f"{current_dir}/template.eds")
        self.network.add_node(self.centerNode)
        self.centerNode.add_write_callback(self.on_write)

    def on_write(self, index, subindex, od, data):
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
            update = upgradeWidget(data[0], data[1], data[2], self.network, self)
            self.controlWidgets[data[0]] = update

            mainlayout.addWidget(
                update,
                idx // 4,
                idx % 4,
            )
            # print(idx, data)

        self.setLayout(mainlayout)

    @Slot(str)
    def on_path_update(self, path):
        files = os.listdir(path)

        bins = [file for file in files if file.endswith(".bin")]
        # print(bins)

        for bin in bins:
            prefix = bin.split(".")[0]

            item = [data for data in datas if data[2] == prefix]
            if len(item) == 0:
                continue
            cid, _, _ = item[0]
            # print(hex(cid), os.path.abspath(bin))

            self.controlWidgets[cid].on_file_update(os.path.join(path, bin))
