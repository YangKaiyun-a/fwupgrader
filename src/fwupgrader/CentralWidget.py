import os
import struct

import canopen
from PySide6 import QtWidgets
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QApplication,
    QFileDialog, QMessageBox, QCheckBox, QTableWidgetItem
)
from apt.auth import update

from src.fwupgrader.Data.DataSet import parse_update_file, get_new_version_from_file
from src.fwupgrader.Data.Global import ComponentType, lower_module_datas, ResultType
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Data.UpgradeThread import UpgradeThread
from src.fwupgrader.Module.GeneralData import GeneralData
from src.fwupgrader.Module.LowerData import LowerData


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.upgrade_thread = None
        self.tableWidget = None
        self.content_vlayout = None
        self.btnUpdate = None           # 升级按钮
        self.btnImport = None           # 导入升级包按钮
        self.btnBack = None             # 推出按钮

        self.upper_data = None          # 存储上位机升级数据
        self.middle_data = None         # 存储中位机升级数据
        self.qpcr_data = None           # 存储QPCR升级数据
        self.checkBox_map = {}          # 存储上位机、中位机、QPCR的QCheckBox
        self.data_list = []             # 根据索引值存储上位机、中位机、QPCR

        self.centerNode = None
        self.network = None             # Can网络
        self.lower_module_list = {}     # 根据cob_id存储固件模块
        self.checkBox_lower_map = {}    # 存储固件模块的QCheckBox

        self.init()

    def init(self):
        self.init_data()
        self.init_ui()
        self.init_connect()

    def init_data(self):
        """初始化数据"""
        self.initCanNetwork()

        self.upper_data = GeneralData(ComponentType.Upper)
        self.middle_data = GeneralData(ComponentType.Middle)
        self.qpcr_data = GeneralData(ComponentType.QPCR)
        self.data_list = [self.upper_data, self.middle_data, self.qpcr_data]

    def initCanNetwork(self):
        """初始化Can网络"""
        self.network = canopen.Network()
        # self.network.connect(channel="can0", bustype="socketcan")

        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # 创建一个本地节点，节点 ID 为 0x01，并加载 EDS 文件描述节点
        self.centerNode = canopen.LocalNode(0x01, f"{current_dir}/template.eds")
        self.network.add_node(self.centerNode)

        # 设置一个回调函数，在收到 CANopen 网络写入数据时调用
        self.centerNode.add_write_callback(self.on_write)

        # 初始化固件模块
        for index, module in enumerate(lower_module_datas):
            # 创建每个固件，并根据cob_id存储在ModuleList容器中
            data = LowerData(module[0], module[1], self.network)
            self.lower_module_list[module[0]] = data

    # 初始化ui
    def init_ui(self):
        top_widget = QWidget()
        top_widget.setObjectName("top_widget")
        top_widget.setStyleSheet("QWidget#top_widget {border: 1px solid black;}")

        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_widget.setStyleSheet("QWidget#content_widget {border: 1px solid blue;}")

        # 导入按钮
        self.btnImport = QPushButton("导入升级包")
        self.btnImport.setFixedSize(150, 50)
        self.btnImport.clicked.connect(self.onBtnImportClicked)

        # 升级按钮
        self.btnUpdate = QPushButton("升级")
        self.btnUpdate.setFixedSize(150, 50)
        self.btnUpdate.clicked.connect(self.onBtnUpdateClicked)

        # 返回按钮
        self.btnBack = QPushButton("退出")
        self.btnBack.setFixedSize(150, 50)
        self.btnBack.clicked.connect(self.onBtnBackClicked)

        # top_widget布局
        top_hlayout = QHBoxLayout(top_widget)
        top_hlayout.addStretch()
        top_hlayout.addWidget(self.btnImport)
        top_hlayout.addWidget(self.btnUpdate)
        top_hlayout.addWidget(self.btnBack)

        # content_widget布局
        self.content_vlayout = QHBoxLayout(content_widget)
        self.content_vlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_vlayout.setContentsMargins(0, 0, 0, 0)

        self.init_tableWidget()

        # 主布局
        main_vlayout = QVBoxLayout(self)
        main_vlayout.addWidget(top_widget, stretch=1)
        main_vlayout.addWidget(content_widget, stretch=10)

    def init_tableWidget(self):
        """初始化表格"""
        row_count = len(self.data_list) + len(self.lower_module_list)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(row_count)

        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 280)
        self.tableWidget.setColumnWidth(2, 420)
        self.tableWidget.setColumnWidth(3, 420)
        self.tableWidget.setColumnWidth(4, 170)

        # 设置每行的高度
        for row in range(row_count):
            self.tableWidget.setRowHeight(row, 45)

        # 设置水平表头
        horizontal_headers = ["", "部件", "当前版本", "最新版本", "状态"]
        self.tableWidget.setHorizontalHeaderLabels(horizontal_headers)

        # 隐藏竖直表头
        vertical_header = self.tableWidget.verticalHeader()
        vertical_header.setVisible(False)

        # 设置表格为不可编辑
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 将第一列全设为QCheckBox
        for row in range(row_count):
            checkbox = QCheckBox()
            checkbox.setEnabled(False)  # 默认不可勾选，等导入文件后才可勾选
            container_widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container_widget.setLayout(layout)
            self.tableWidget.setCellWidget(row, 0, container_widget)

            if row <= ComponentType.QPCR.value:
                self.checkBox_map[row] = checkbox
            else:
                lower_row_index = row - 3
                if lower_row_index < len(lower_module_datas):
                    self.checkBox_lower_map[lower_module_datas[lower_row_index][0]] = checkbox

        self.init_tableWidget_item()

        self.content_vlayout.addWidget(self.tableWidget)

    def init_tableWidget_item(self):
        # 设置上位机、中位机、QPCR
        for row, data in enumerate(self.data_list):
            self.set_tableWidget_item(row, data)

        # 设置固件模块
        for row, cob_id in enumerate(self.lower_module_list, start=len(self.data_list)):
            module = self.lower_module_list[cob_id]
            self.set_tableWidget_item(row, module)

    def set_tableWidget_item(self, row, module):
        # 第二列，显示部件中文名
        item = QTableWidgetItem(module.get_component_type_name())
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row, 1, item)

        # 第三列，显示当前版本
        item = QTableWidgetItem(module.get_current_version())
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row, 2, item)

        # 第四列，显示最新版本
        item = QTableWidgetItem(module.get_new_version())
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row, 3, item)

        # 第五列，设置状态
        item = QTableWidgetItem(module.get_status())
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row, 4, item)

    def init_connect(self):
        signal_manager.sigUpdateFileAddress.connect(self.onSigUpdateFileAddress)
        signal_manager.sigUpdateLowerAddress.connect(self.onSigUpdateLowerAddress)
        signal_manager.sigExecuteScriptResult.connect(self.onSigExecuteScriptResult)

    def get_checked_component(self):
        """获取当前要升级的部件"""
        checked_component_list = []
        for index, checkbox in self.checkBox_map.items():
            if checkbox.isChecked():
                checked_component_list.append(index)

        checked_lower_component_list = []
        for index, checkbox in self.checkBox_lower_map.items():
            if checkbox.isChecked():
                checked_lower_component_list.append(index)

        return checked_component_list, checked_lower_component_list

    @Slot()
    def onSigUpdateLowerAddress(self, bin_file_dict):
        """接收固件升级路径"""
        if not bin_file_dict:
            QMessageBox.warning(self, "警告", "固件文件解析为空，请检查路径！", QMessageBox.StandardButton.Ok)
            return

        for file_name, file_path in bin_file_dict.items():
            prefix = file_name.split(".")[0]
            new_version = get_new_version_from_file(ComponentType.Lower, file_name)
            item = [data for data in lower_module_datas if data[2] == prefix]

            if len(item) == 0:
                continue

            cid, _, _ = item[0]

            # 更新每个固件的地址
            self.lower_module_list[cid].on_file_update(file_path, new_version)

        self.init_tableWidget_item()

    def on_write(self, index, subindex, od, data):
        # 解包收到的二进制数据，将其解析为两个 16 位无符号整数，分别为 value 和 cob_id
        value, cob_id = struct.unpack("HH", data)

        print(f"codid {cob_id} index {hex(index)} subindex{hex(subindex)} value {value}")

        for _, w in self.lower_module_list.items():
            if w.in_process:
                w.receive_module_reply(index, subindex, value)
                break

    @Slot()
    def onSigExecuteScriptResult(self, machine_type, result):
        """升级结果槽函数"""
        message1 = ""
        if result == ResultType.SUCCESSED:
            message1 = "升级成功"
        elif result == ResultType.FAILD:
            message1 = "升级失败"
        elif result == ResultType.START:
            message1 = "正在升级中"

    @Slot()
    def onSigUpdateFileAddress(self, computer_type, file_absolute_path):
        """接收上位机，中位机，QPCR升级路径"""
        component = self.data_list[computer_type]
        component.update_file_info(file_absolute_path)

        if component.get_current_version() == "获取失败":
            self.checkBox_map[computer_type].setEnabled(False)
        elif component.get_current_version() == component.get_new_version():
            self.checkBox_map[computer_type].setEnabled(False)
        else:
            self.checkBox_map[computer_type].setEnabled(True)

        self.init_tableWidget_item()

    @Slot()
    def onBtnImportClicked(self):
        """导入按钮槽函数"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择升级文件包",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if not directory:
            QMessageBox.warning(self, "警告", "请选择路径！", QMessageBox.StandardButton.Ok)
            return

        parse_update_file(directory)

    @Slot()
    def onBtnUpdateClicked(self):
        """升级按钮槽函数"""
        update_components = []
        checked_component_list, checked_lower_component_list = self.get_checked_component()

        # 收集要升级的部件
        for index in checked_component_list:
            data_object = self.data_list[index]
            update_components.append(data_object)

        # 收集要升级的固件
        for index in checked_lower_component_list:
            data_object = self.lower_module_list[index]
            update_components.append(data_object)

        if not update_components:
            QMessageBox.warning(self, "警告", "请选择要升级的部件或固件", QMessageBox.StandardButton.Ok)
            return 

        # 串行执行升级
        self.upgrade_thread = UpgradeThread(update_components)
        self.upgrade_thread.start()

    @Slot()
    def onBtnBackClicked(self):
        """返回按钮槽函数"""
        QApplication.quit()


