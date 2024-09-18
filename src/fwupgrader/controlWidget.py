from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QProgressBar,
    QVBoxLayout,
    QDialog,
    QMessageBox,
)

from PySide6.QtCore import Qt, QTimer, QThread, Slot, Signal
import canopen
import os
import hashlib
import time
import threading


# 更新进度条显示框
class ProgressDialog(QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"{name} 升级")
        self.setGeometry(200, 200, 300, 100)

        layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # 屏蔽esc键

    @Slot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @Slot()
    def finish(self):
        self.close()


class UpgradeThread(QThread):
    # 用于发送进度百分比信号
    present = Signal(int)
    # 用于通知升级完成
    finish = Signal()

    def __init__(self, remote, fw, parent=None):
        super().__init__(parent)
        self.remote = remote
        self.fw = fw  # 固件文件路径
        self.semaphore = threading.Semaphore(0)
        self.success = False

    @Slot(bool)
    def on_reply(self, r):
        print('----------', r)
        self.success = r
        self.semaphore.release()

    def run(self):
        # 读取固件文件，r：只读，b：二进制
        with open(self.fw, "rb") as f:
            fw_data = f.read()

        # 计算固件文件的MD5值
        m = hashlib.md5()
        m.update(fw_data)

        try:
            # 向远程设备发送MD5和大小
            print(f"发送MD5：{m.hexdigest()}")
            self.remote.sdo["iap"]["md5"].raw = m.digest()

            print(f"发送文件大小：{len(fw_data)} KB")
            self.remote.sdo["iap"]["size"].raw = len(fw_data)

            self.success = True
        except Exception as e:
            print("参数发送错误")
            self.success = False

        # 如果参数发送失败，终止升级
        if not self.success:
            self.finish.emit()
            return

        print("开始发送数据")

        # 分块发送固件数据，每块32字节
        frames = [fw_data[i: i + 32] for i in range(0, len(fw_data), 32)]
        total = len(frames)
        print(f"将文件分为{total}块")

        for idx, f in enumerate(frames):
            try:
                # 设置偏移
                self.remote.sdo["iap"]["offset"].raw = idx * 32
                print(f"offset: {idx * 32}")
                # 发送数据块
                self.remote.sdo["iap"]["data"].raw = f
                print(f"data: {f}")
            except Exception as e:
                self.success = False

            if not self.success:
                break

            # 等待应答信号，如果超时则终止
            if self.semaphore.acquire(timeout=10) == False:
                self.success = False
                break

            self.present.emit(int((idx / total) * 100))

        self.finish.emit()


class UpgradeWidget(QWidget):
    sig = Signal(bool)
    reply = Signal(bool)

    def __init__(self, cob_id, name, tag, network, parent=None):
        super().__init__(parent)
        self.getVersionButton = None    # 固件更新按钮
        self.updateButton = None        # 获取版本按钮
        self.cob_id = cob_id            # 设备ID
        self.name = name                # 设备名称
        self.tag = tag                  # 设备标识
        self.fw = None                  # 固件文件路径
        self.in_process = False         # 是否在升级中

        # 添加远程节点到CANopen网络
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.remote = canopen.RemoteNode(cob_id, f"{current_dir}/template.eds")
        network.add_node(self.remote)

        self.initUI()

    def initUI(self):
        self.updateButton = QPushButton("固件更新")
        self.getVersionButton = QPushButton("获取版本")

        self.updateButton.clicked.connect(self.update_fw)
        self.getVersionButton.clicked.connect(self.upgradeButtonClicked)

        gridLayout = QGridLayout()

        tag = QLabel(f"{self.name}:[{hex(self.cob_id)}]", self)
        tag.setStyleSheet("color: green")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.old_version = QLabel("旧版本")
        self.new_version = QLabel("新版本")

        gridLayout.addWidget(tag, 0, 0, 1, 2)
        gridLayout.addWidget(QLabel("初始:", self), 1, 0)
        gridLayout.addWidget(QLabel("固件:", self), 2, 0)

        gridLayout.addWidget(self.old_version, 1, 1)
        gridLayout.addWidget(self.new_version, 2, 1)
        gridLayout.addWidget(self.updateButton, 3, 0, 1, 2)
        gridLayout.addWidget(self.getVersionButton, 4, 0, 1, 2)
        self.setLayout(gridLayout)

    # 固件更新
    def update_fw(self):
        process = ProgressDialog(self.fw, self)

        if self.fw is None:
            msg = QMessageBox()
            msg.setText("请选择固件路径")
            msg.exec()
            return

        # 开启线程
        p = UpgradeThread(self.remote, self.fw, self)
        p.present.connect(process.update_progress)
        p.finish.connect(process.finish)
        self.reply.connect(p.on_reply)
        p.start()
        self.in_process = True
        process.exec()

        self.in_process = False

        self.reply.disconnect(p.on_reply)
        print("结束了")
        text = "升级成功" if p.success else "升级失败"

        msg = QMessageBox()
        msg.setText(text)
        msg.exec()

    # 获取版本
    def update_version(self):
        ver = "未获取到"

        success = False

        try:
            num = self.remote.sdo["module_version"]["version_num"].raw
            ver = f"{num >> 24}.{(num >> 16) & 0xFF}.{(num >> 8) & 0xFF}.{num & 0xFF}"
            success = True

        except Exception as e:
            print(e)

        self.old_version.setText(ver)

        self.old_version.setStyleSheet(
            "color: red"
        ) if not success else self.old_version.setStyleSheet("color: green")

    # 获取版本
    def upgradeButtonClicked(self):
        self.update_version()

    def on_reply(self, index, subindex, value):
        self.reply.emit(True)

    def on_file_update(self, path):
        self.fw = path
        self.new_version.setText(os.path.basename(path))

        print(f"fw: {self.fw}")
