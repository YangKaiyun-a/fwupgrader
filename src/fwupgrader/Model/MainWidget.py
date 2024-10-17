import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QCheckBox, QTableWidgetItem, QVBoxLayout, QMessageBox
)

from src.fwupgrader.CustomControls.MessageDlg import MessageDlg
from src.fwupgrader.Data.DataSet import ComputerType, ResultType
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Model.GeneralData.GeneralData import GeneralData


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mainLayout = None
        self.tableWidget = None
        self.upper_data = None      # 存储上位机升级数据
        self.middle_data = None     # 存储中位机升级数据
        self.upper_current_version_item = None      # 表格中上位机当前版本号的item
        self.middle_current_version_item = None     # 表格中中位机当前版本号的item
        self.upper_new_version_item = None          # 表格中上位机新版本号的item
        self.middle_new_version_item = None         # 表格中中位机新版本号的item
        self.btn_update = None                      # 升级按钮
        self.checkBoxMap = {}                       # 存储每个QCheckBox
        self.result_dlg = None                      # 升级提示框

        self.init_data()
        self.init_ui()
        self.init_connect()

    def init_ui(self):
        """初始化ui"""
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)

        self.init_tableWidget()

        self.btn_update = QPushButton("升级")
        self.btn_update.setFixedSize(135, 45)
        self.btn_update.clicked.connect(self.onBtnUpdateClicked)
        self.btn_update.setEnabled(False)

        self.result_dlg = MessageDlg("", self)

        self.mainLayout.addWidget(self.btn_update)

    def init_tableWidget(self):
        """初始化表格"""
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setFixedSize(1000, 150)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(4)

        self.tableWidget.setColumnWidth(0, 50)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 370)
        self.tableWidget.setColumnWidth(3, 370)

        # 设置水平表头
        horizontal_headers = ["", "部件", "当前版本", "最新版本"]
        self.tableWidget.setHorizontalHeaderLabels(horizontal_headers)

        # 隐藏竖直表头
        vertical_header = self.tableWidget.verticalHeader()
        vertical_header.setVisible(False)

        # 将第一列全设为QCheckBox
        for row in range(self.tableWidget.rowCount()):
            checkbox = QCheckBox()
            checkbox.clicked.connect(self.onCheckBoxClicked)
            container_widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(checkbox)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            container_widget.setLayout(layout)
            self.tableWidget.setCellWidget(row, 0, container_widget)
            self.checkBoxMap[row] = checkbox

        # 设置第二列
        components = ["上位机", "中位机", "QPCR", "固件模块"]
        for row, component in enumerate(components):
            item = QTableWidgetItem(component)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tableWidget.setItem(row, 1, item)

        # 设置第三列
        self.set_current_version()

        # 设置第四列
        self.set_new_version()

        self.mainLayout.addWidget(self.tableWidget)

    def init_data(self):
        """初始化数据"""
        self.upper_data = GeneralData(ComputerType.Upper)
        self.middle_data = GeneralData(ComputerType.Middle)

    def init_connect(self):
        signal_manager.sigUpdateUpperAddress.connect(self.onSigUpdateUpperAddress)
        signal_manager.sigUpdateMiddleAddress.connect(self.onSigUpdateMiddleAddress)
        signal_manager.sigExecuteScriptResult.connect(self.onSigExecuteScriptResult)

    def set_current_version(self):
        """每次进入该页面时会调用这个刷新函数，设置当前版本"""
        # 设置表格第三列，当前版本号
        self.set_current_upper_version()
        # self.set_middle_current_version()


    def set_new_version(self):
        """设置第四列，新版本号"""
        self.set_new_upper_version()
        # self.set_new_middle_current_version()



    def set_current_upper_version(self):
        """设置上位机当前版本号"""
        self.upper_data.get_current_version()

        self.upper_current_version_item = QTableWidgetItem(self.upper_data.current_version)
        self.upper_current_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(0, 2, self.upper_current_version_item)

    def set_middle_current_version(self):
        """设置中位机当前版本号"""
        self.middle_current_version_item = QTableWidgetItem(self.middle_data.current_version)
        self.middle_current_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(1, 4, self.middle_current_version_item)

    def set_new_upper_version(self):
        """设置上位机新版本号"""
        self.upper_new_version_item = QTableWidgetItem(self.upper_data.new_version)
        self.upper_new_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(0, 3, self.upper_new_version_item)

    def set_new_middle_current_version(self):
        """设置中位机新版本号"""
        self.middle_new_version_item = QTableWidgetItem(self.middle_data.new_version)
        self.middle_new_version_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(1, 3, self.middle_new_version_item)

    def get_checked_rows(self):
        """获取当前要升级的部件"""
        checked_rows = []
        for row, checkbox in self.checkBoxMap.items():
            if checkbox.isChecked():
                checked_rows.append(ComputerType(row))
        return checked_rows

    def upper_machine_update(self):
        """执行上位机升级"""
        result = self.upper_data.update_machine()
        if result == ResultType.Empty_File_path:
            QMessageBox.warning(self, "警告", "请导入升级包", QMessageBox.StandardButton.Ok)
        elif result == ResultType.Start_Update:
            self.result_dlg.setText("正在升级，请稍候...")
            self.result_dlg.setBtnEnabled(False)
            self.result_dlg.exec_()

    def middle_machine_update(self):
        """执行中位机升级"""
        pass

    def qpcr_machine_update(self):
        """执行QPCR升级"""
        pass

    def lower_machine_update(self):
        """执行固件升级"""
        pass

    @Slot()
    def onBtnUpdateClicked(self):
        """升级按钮槽函数"""
        update_components = self.get_checked_rows()

        for machine_type in update_components:
            if machine_type  == ComputerType.Upper:
                self.upper_machine_update()
            elif machine_type == ComputerType.Middle:
                self.middle_machine_update()
            elif machine_type == ComputerType.QPCR:
                self.qpcr_machine_update()


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
        signal_manager.sigSwitchPage.emit(3)

    @Slot()
    def onSigUpdateUpperAddress(self, file_absolute_path):
        """接收上位机升级路径"""
        self.upper_data.update_file_info(file_absolute_path)
        self.set_new_upper_version()

    @Slot()
    def onSigUpdateMiddleAddress(self, file_absolute_path):
        """接收中位机升级路径"""
        self.middle_data.update_file_info(file_absolute_path)

    @Slot()
    def onSigExecuteScriptResult(self, message):
        """升级结果槽函数"""





