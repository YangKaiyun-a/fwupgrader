import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QCheckBox, QTableWidgetItem, QVBoxLayout, QMessageBox
)

from src.fwupgrader.Data.Global import ComputerType, ResultType
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Data.UpgradeThread import UpgradeThread
from src.fwupgrader.Module.GeneralData.GeneralData import GeneralData


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
        self.upper_current_version_item = None      # 表格中上位机当前版本号的item
        self.middle_current_version_item = None     # 表格中中位机当前版本号的item
        self.qpcr_current_version_item = None       # 表格中QPCR当前版本号的item
        self.upper_new_version_item = None          # 表格中上位机新版本号的item
        self.middle_new_version_item = None         # 表格中中位机新版本号的item
        self.qpcr_new_version_item = None           # 表格中QPCR新版本号的item
        self.upper_status_item = None               # 表格中上位机状态的item
        self.middle_status_item = None              # 表格中中位机状态的item
        self.qpcr_status_item = None                # 表格中QPCR状态的item
        self.btn_update = None                      # 升级按钮
        self.checkBoxMap = {}                       # 存储每个QCheckBox
        self.data_Map = {}                          # ComputerType索引值与GeneralData的对应关系

        self.init_data()
        self.init_ui()
        self.init_connect()

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

        self.btn_lower = QPushButton("固件模块升级")
        self.btn_lower.setFixedSize(135, 45)
        self.btn_lower.clicked.connect(self.onBtnLowerClicked)

        button_hlayout.setSpacing(9)
        button_hlayout.addWidget(self.btn_update)
        button_hlayout.addWidget(self.btn_lower)
        button_widget.setLayout(button_hlayout)

        self.mainLayout.addWidget(button_widget)

    def init_tableWidget(self):
        """初始化表格"""
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setFixedSize(1100, 151)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(3)

        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 370)
        self.tableWidget.setColumnWidth(3, 370)
        self.tableWidget.setColumnWidth(4, 100)

        self.tableWidget.setRowHeight(0, 41)
        self.tableWidget.setRowHeight(1, 41)
        self.tableWidget.setRowHeight(2, 41)

        # 设置水平表头
        horizontal_headers = ["", "部件", "当前版本", "最新版本", "状态"]
        self.tableWidget.setHorizontalHeaderLabels(horizontal_headers)

        # 隐藏竖直表头
        vertical_header = self.tableWidget.verticalHeader()
        vertical_header.setVisible(False)

        # 设置表格为不可编辑
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 将第一列全设为QCheckBox
        for row in range(self.tableWidget.rowCount()):
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
            self.checkBoxMap[ComputerType(row)] = checkbox

        # 设置第二列
        components = ["上位机", "中位机", "QPCR"]
        for row, component in enumerate(components):
            item = QTableWidgetItem(component)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(row, 1, item)

        # 设置第三列
        self.init_current_version()

        # 设置第四列
        self.init_new_version()

        # 设置第五列
        self.upper_status_item = QTableWidgetItem("---")
        self.upper_status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(0, 4, self.upper_status_item)

        self.middle_status_item = QTableWidgetItem("---")
        self.middle_status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(1, 4, self.middle_status_item)

        self.qpcr_status_item = QTableWidgetItem("---")
        self.qpcr_status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(2, 4, self.qpcr_status_item)

        self.mainLayout.addWidget(self.tableWidget)

    def init_data(self):
        """初始化数据"""
        self.upper_data = GeneralData(ComputerType.Upper)
        self.middle_data = GeneralData(ComputerType.Middle)
        self.qpcr_data = GeneralData(ComputerType.QPCR)

        self.data_Map = {
            ComputerType.Upper: self.upper_data,
            ComputerType.Middle: self.middle_data,
            ComputerType.QPCR: self.qpcr_data
        }

    def init_connect(self):
        signal_manager.sigUpdateUpperAddress.connect(self.onSigUpdateUpperAddress)
        signal_manager.sigUpdateMiddleAddress.connect(self.onSigUpdateMiddleAddress)
        signal_manager.sigUpdateQPCRAddress.connect(self.onSigUpdateQPCRAddress)
        signal_manager.sigExecuteScriptResult.connect(self.onSigExecuteScriptResult)

    def init_current_version(self):
        """设置当前版本设置表格第三列，当前版本号"""
        self.init_current_upper_version()
        self.init_current_middle_version()
        self.init_current_qpcr_version()

    def init_new_version(self):
        """设置第四列，新版本号"""
        self.init_new_upper_version()
        self.init_new_middle_version()
        self.init_new_qpcr_version()

    def init_current_upper_version(self):
        """初始化上位机当前版本号"""
        self.upper_current_version_item = QTableWidgetItem(self.upper_data.get_current_version())
        self.upper_current_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(0, 2, self.upper_current_version_item)

    def init_current_middle_version(self):
        """初始化中位机当前版本号"""
        self.middle_current_version_item = QTableWidgetItem(self.middle_data.get_current_version())
        self.middle_current_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(1, 2, self.middle_current_version_item)

    def init_current_qpcr_version(self):
        """初始化QPCR当前版本号"""
        self.qpcr_current_version_item = QTableWidgetItem(self.middle_data.get_current_version())
        self.qpcr_current_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(2, 2, self.qpcr_current_version_item)

    def init_new_upper_version(self):
        """初始化上位机新版本号"""
        self.upper_new_version_item = QTableWidgetItem(self.upper_data.get_new_version())
        self.upper_new_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(0, 3, self.upper_new_version_item)

    def init_new_middle_version(self):
        """初始化中位机新版本号"""
        self.middle_new_version_item = QTableWidgetItem(self.middle_data.get_new_version())
        self.middle_new_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(1, 3, self.middle_new_version_item)

    def init_new_qpcr_version(self):
        """初始化QPCR新版本号"""
        self.qpcr_new_version_item = QTableWidgetItem(self.middle_data.get_new_version())
        self.qpcr_new_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(2, 3, self.qpcr_new_version_item)

    def set_current_upper_version(self):
        """设置上位机当前版本号"""
        self.upper_current_version_item.setText(self.upper_data.get_current_version())

    def set_new_upper_version(self):
        """设置上位机新版本号"""
        self.upper_new_version_item.setText(self.upper_data.get_new_version())

    def set_current_middle_version(self):
        """设置中位机当前版本号"""
        self.middle_current_version_item.setText(self.middle_data.get_current_version())

    def set_new_middle_version(self):
        """设置中位机新版本号"""
        self.middle_new_version_item.setText(self.middle_data.get_new_version())

    def set_current_qpcr_version(self):
        """设置QPCR当前版本号"""
        self.qpcr_new_version_item.setText(self.middle_data.get_new_version())

    def set_new_qpcr_version(self):
        """设置QPCR新版本号"""
        self.qpcr_new_version_item.setText(self.middle_data.get_new_version())

    def get_checked_rows(self):
        """获取当前要升级的部件"""
        checked_rows = []
        for row, checkbox in self.checkBoxMap.items():
            if checkbox.isChecked():
                checked_rows.append(ComputerType(row))
        return checked_rows

    @Slot()
    def onBtnUpdateClicked(self):
        """升级按钮槽函数"""
        update_components = []
        error_message = []

        for machine_type in self.get_checked_rows():
            data_object = self.data_Map.get(machine_type)
            if data_object and not data_object.get_fw():
                error_message.append(data_object.get_computer_type_name())
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
        checked_count = sum(1 for checkbox in self.checkBoxMap.values() if checkbox.isChecked())
        if checked_count == 0:
            self.btn_update.setEnabled(False)
        elif checked_count > 0:
            self.btn_update.setEnabled(True)

    @Slot()
    def onBtnLowerClicked(self):
        """下位机升级按钮槽函数"""
        signal_manager.sigSwitchPage.emit(1)

    @Slot()
    def onSigUpdateUpperAddress(self, file_absolute_path):
        """接收上位机升级路径"""
        self.upper_data.update_file_info(file_absolute_path)
        self.set_new_upper_version()

        if self.upper_data.get_current_version() == self.upper_data.get_new_version():
            self.upper_status_item.setText("无需升级")
            self.checkBoxMap[ComputerType.Upper].setEnabled(False)
        else:
            self.upper_status_item.setText("可升级")
            self.checkBoxMap[ComputerType.Upper].setEnabled(True)

    @Slot()
    def onSigUpdateMiddleAddress(self, file_absolute_path):
        """接收中位机升级路径"""
        self.middle_data.update_file_info(file_absolute_path)
        self.set_new_middle_version()

        if self.middle_data.get_current_version() == self.middle_data.get_new_version():
            self.middle_status_item.setText("无需升级")
            self.checkBoxMap[ComputerType.Middle].setEnabled(False)
        else:
            self.middle_status_item.setText("可升级")
            self.checkBoxMap[ComputerType.Middle].setEnabled(True)

    @Slot()
    def onSigUpdateQPCRAddress(self, file_absolute_path):
        """接收QPCR升级路径"""
        self.qpcr_data.update_file_info(file_absolute_path)
        self.set_new_qpcr_version()

        if self.qpcr_data.get_current_version() == self.qpcr_data.get_new_version():
            self.qpcr_status_item.setText("无需升级")
            self.checkBoxMap[ComputerType.QPCR].setEnabled(False)
        else:
            self.qpcr_status_item.setText("可升级")
            self.checkBoxMap[ComputerType.QPCR].setEnabled(True)

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

        if machine_type == ComputerType.Upper:
            self.set_current_upper_version()
            self.upper_status_item.setText(message1)
        elif machine_type == ComputerType.Middle:
            self.set_current_middle_version()
            self.middle_status_item.setText(message1)
        elif machine_type == ComputerType.QPCR:
            self.set_current_qpcr_version()
            self.qpcr_status_item.setText(message1)










