import os
import struct

import canopen
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QCheckBox, QTableWidgetItem, QVBoxLayout, QMessageBox
)

from src.fwupgrader.Data.DataSet import get_new_version_from_file
from src.fwupgrader.Data.Global import ComponentType, ResultType, lower_module_datas
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Data.UpgradeThread import UpgradeThread
from src.fwupgrader.Module.GeneralData.GeneralData import GeneralData
from src.fwupgrader.Module.Lower.LowerData import LowerData


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.upgrade_thread = None                  # 维持线程持久化
        self.mainLayout = None                      # 主布局
        self.tableWidget = None                     # 表格
        self.upper_data = None                      # 存储上位机升级数据
        self.middle_data = None                     # 存储中位机升级数据
        self.qpcr_data = None                       # 存储QPCR升级数据
        self.btn_lower = None                       # 固件模块升级按钮
        self.upper_status_item = None               # 表格中上位机状态的item
        self.middle_status_item = None              # 表格中中位机状态的item
        self.qpcr_status_item = None                # 表格中QPCR状态的item
        self.btn_update = None                      # 升级按钮
        self.checkBox_map = {}                      # 存储上位机、中位机、QPCR的QCheckBox
        self.data_list = []                         # 根据索引值存储上位机、中位机、QPCR

        self.centerNode = None
        self.network = None                         # Can网络
        self.lower_module_list = None               # 根据cob_id存储固件模块
        self.checkBox_lower_map = {}                # 存储固件模块的QCheckBox

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
        for module in enumerate(lower_module_datas):
            # 创建每个固件，并根据cob_id存储在ModuleList容器中
            data = LowerData(module[0], module[1], module[2], self.network)
            self.lower_module_list[module[0]] = data

    def init_ui(self):
        """初始化ui"""
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(9)
        self.setLayout(self.mainLayout)

        self.init_tableWidget()

        button_widget = QWidget()
        button_widget.setFixedHeight(60)
        button_hlayout = QtWidgets.QHBoxLayout()
        button_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_update = QPushButton("升级")
        self.btn_update.setFixedSize(135, 45)
        self.btn_update.clicked.connect(self.onBtnUpdateClicked)
        self.btn_update.setEnabled(False)

        button_hlayout.setSpacing(9)
        button_hlayout.addWidget(self.btn_update)
        button_hlayout.addWidget(self.btn_lower)
        button_widget.setLayout(button_hlayout)

        self.mainLayout.addWidget(button_widget)

    def init_tableWidget(self):
        """初始化表格"""
        row_count = len(self.data_list) + len(self.lower_module_list)
        tableWidget_height = row_count * 41 + 28

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setFixedSize(1100, tableWidget_height)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(row_count)

        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 370)
        self.tableWidget.setColumnWidth(3, 370)
        self.tableWidget.setColumnWidth(4, 100)

        # 设置每行的高度
        for row in range(row_count):
            self.tableWidget.setRowHeight(row, 41)

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
            checkbox.clicked.connect(self.onCheckBoxClicked)
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

        # 设置上位机、中位机、QPCR
        for row, data in enumerate(self.data_list):
            self.set_table_widget_item(row, data)

        # 设置固件模块
        for row, module in enumerate(self.lower_module_list, start=len(self.data_list) + 1):
            self.set_table_widget_item(row, module)

        self.mainLayout.addWidget(self.tableWidget)

    def set_table_widget_item(self, row, module):
        # 第二列，显示部件中文名
        item = QTableWidgetItem(module.get_name())
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
        item = QTableWidgetItem("---")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row, 4, item)

    def init_connect(self):
        signal_manager.sigUpdateFileAddress.connect(self.onSigUpdateFileAddress)
        signal_manager.sigUpdateLowerAddress.connect(self.onSigUpdateLowerAddress)
        signal_manager.sigExecuteScriptResult.connect(self.onSigExecuteScriptResult)

    def set_component_status(self, component_type, status_str):
        """设置上位机、中位机、QPCR的状态"""
        if component_type == ComponentType.Upper:
            self.upper_status_item.setText(status_str)
        elif component_type == ComponentType.Middle:
            self.middle_status_item.setText(status_str)
        elif component_type == ComponentType.QPCR:
            self.qpcr_status_item.setText(status_str)

    def show_current_single_version(self, component_type):
        """显示单个部件的当前版本号"""
        pass

    def show_new_single_version(self, component_type):
        """显示单个部件的最新版本号"""
        pass

    def show_current_version(self):
        """显示上位机、中位机、QPCR当前版本号"""
        self.show_current_single_version(ComponentType.Upper)
        self.show_current_single_version(ComponentType.Middle)
        self.show_current_single_version(ComponentType.QPCR)

    def show_new_version(self):
        """显示上位机、中位机、QPCR最新版本号"""
        self.show_new_single_version(ComponentType.Upper)
        self.show_new_single_version(ComponentType.Middle)
        self.show_new_single_version(ComponentType.QPCR)

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
    def onBtnUpdateClicked(self):
        """升级按钮槽函数"""
        update_components = []
        error_message = []

        checked_component_list, checked_lower_component_list = self.get_checked_component()

        # 收集要升级的部件
        for checked_component in checked_component_list:
            data_object = self.data_list[checked_component]
            if data_object and not data_object.get_fw():
                error_message.append(data_object.get_computer_type_name())
            else:
                update_components.append(data_object)

        # 收集要升级的固件
        for checked_lower_component in checked_lower_component_list:
            data_object = self.lower_module_list[checked_lower_component]
            if data_object and not data_object.get_fw():
                error_message.append(data_object.get_name())
            else:
                update_components.append(data_object)

        if error_message:
            error_message_str = '、'.join(error_message)
            QMessageBox.warning(self, "警告", f"未导入{error_message_str}升级包", QMessageBox.StandardButton.Ok)
            return

        # 串行执行升级
        self.upgrade_thread = UpgradeThread(update_components)
        self.upgrade_thread.start()

        # 升级按钮不可点击
        self.btn_update.setEnabled(False)

    @Slot()
    def onCheckBoxClicked(self):
        """每次勾选框状态变化都会触发"""
        checked_count = sum(1 for checkbox in self.checkBox_map.values() if checkbox.isChecked())
        if checked_count == 0:
            self.btn_update.setEnabled(False)
        elif checked_count > 0:
            self.btn_update.setEnabled(True)

    @Slot()
    def onSigUpdateFileAddress(self, computer_type, file_absolute_path):
        """接收上位机，中位机，QPCR升级路径"""
        component = self.data_list[computer_type]

        component.update_file_info(file_absolute_path)
        self.show_new_single_version(computer_type)

        if component.get_current_version() == "获取失败":
            self.set_component_status(computer_type, "异常")
            self.checkBox_map[computer_type].setEnabled(False)
        elif component.get_current_version() == component.get_new_version():
            self.set_component_status(computer_type, "无需升级")
            self.checkBox_map[computer_type].setEnabled(False)
        else:
            self.set_component_status(computer_type, "可升级")
            self.checkBox_map[computer_type].setEnabled(True)

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

        self.show_current_single_version(machine_type)
        self.set_component_status(machine_type, message1)

    def on_write(self, index, subindex, od, data):
        # 解包收到的二进制数据，将其解析为两个 16 位无符号整数，分别为 value 和 cob_id
        value, cob_id = struct.unpack("HH", data)

        print(f"codid {cob_id} index {hex(index)} subindex{hex(subindex)} value {value}")

        for _, w in self.lower_module_list.items():
            if w.in_process:
                w.receive_module_reply(index, subindex, value)
                break








