from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, Slot, QThread
from blueman.plugins.applet.NetUsage import Dialog

from src.fwupgrader.CustomControls.MessageDlg import MessageDlg
from src.fwupgrader.Data.DataSet import get_version, ComputerType, get_version_from_file, execute_upgrade_script
from src.fwupgrader.Data.SignalManager import signal_manager


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


class UpgradeThread(QThread):
    def __init__(self, fw, computer_type, parent=None):
        super().__init__(parent)
        self.fw = fw
        self.computer_type = computer_type

    def run(self):
        execute_upgrade_script(self.fw, self.computer_type)


class GeneralWidget(QWidget):
    def __init__(self, computer_type):
        super().__init__()
        self.computer_type = computer_type  # 区分上位机、中位机
        self.computer_type_name = None  # 字符串，"上位机"或"中位机"
        self.edit_new_version = None  # 最新版本QLinEdit
        self.edit_current_version = None  # 当前版本QLineEdit
        self.fw = None  # 升级文件路径
        self.is_update = False  # 是否在升级过程中
        self.result_dlg = None  # 结果弹窗
        self.init()

    def init(self):
        self.init_ui()
        self.init_connect()

    def init_ui(self):
        """初始化ui"""
        if self.computer_type == ComputerType.Upper:
            self.computer_type_name = '上位机'
        elif self.computer_type == ComputerType.Middle:
            self.computer_type_name = '中位机'

        self.edit_current_version = QLineEdit("Vxx.xx.xx.xxxx")
        self.edit_new_version = QLineEdit("Vxx.xx.xx.xxxx")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        current_version_hlayout = create_version_layout("当前版本：", self.edit_current_version)
        new_version_hlayout = create_version_layout("最新版本：", self.edit_new_version)
        push_button_hlayout = QHBoxLayout()

        btn_update = QPushButton("升级")
        btn_update.setFixedSize(135, 45)
        btn_update.clicked.connect(self.onBtnUpdateClicked)
        push_button_hlayout.addWidget(btn_update)

        main_layout.addStretch()
        main_layout.addLayout(current_version_hlayout)
        main_layout.addLayout(new_version_hlayout)
        main_layout.addLayout(push_button_hlayout)
        main_layout.addStretch()

        self.result_dlg = MessageDlg("", self)

    def init_connect(self):
        signal_manager.sigUpdateUpperAddress.connect(self.onSigUpdateUpperAddress)
        signal_manager.sigUpdateMiddleAddress.connect(self.onSigUpdateMiddleAddress)
        signal_manager.sigExecuteScriptResult.connect(self.onSigExecuteScriptResult)

    def refresh_ui(self):
        """每次进入该页面时会调用这个刷新函数"""
        version = get_version(ComputerType.Upper)
        self.edit_current_version.setText(version)
        print(f"获取到{self.computer_type_name}当前版本为：{version}")

    def clear_file_info(self):
        """清空所有信息"""
        self.fw = None
        self.edit_new_version.setText("Vxx.xx.xx.xxxx")
        self.is_update = False

    @Slot()
    def onSigUpdateUpperAddress(self, file_absolute_path):
        """接收上位机升级路径"""
        if self.computer_type == ComputerType.Middle:
            return

        self.clear_file_info()
        self.fw = file_absolute_path
        new_version = get_version_from_file(file_absolute_path)
        self.edit_new_version.setText(new_version)
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    @Slot()
    def onSigUpdateMiddleAddress(self, file_absolute_path):
        """接收中位机升级路径"""
        if self.computer_type == ComputerType.Upper:
            return

        self.clear_file_info()
        self.fw = file_absolute_path
        new_version = get_version_from_file(file_absolute_path)
        self.edit_new_version.setText(new_version)
        print(f"获取到{self.computer_type_name}最新版本为：{new_version}")

    @Slot()
    def onBtnUpdateClicked(self):
        """升级按钮槽函数"""
        if not self.fw:
            QMessageBox.warning(self, "警告", "请导入升级包", QMessageBox.StandardButton.Ok)
            return

        self.is_update = True
        # 执行升级
        upgrade_thread = UpgradeThread(self.fw, self.computer_type)
        upgrade_thread.start()
        self.result_dlg.setText("正在升级，请稍候...")
        self.result_dlg.setBtnEnabled(False)
        self.result_dlg.exec_()

    @Slot()
    def onSigExecuteScriptResult(self, message):
        """升级结果槽函数"""

        # 通过是否处于升级状态来区分上、中位机
        if not self.is_update:
            return

        self.is_update = False

        self.result_dlg.setText(message)
        self.result_dlg.setBtnEnabled(True)

        self.clear_file_info()
        self.refresh_ui()
