"""
GP固件升级工具
"""
import sys

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    # Backwards compatibility - importlib.metadata was added in Python 3.8
    import importlib_metadata

from PySide6 import QtWidgets
from PySide6.QtCore import Signal

from centerWidget import CenterWidget


# FwUpgrader类继承于QtWidgets.QMainWindow
class FwUpgrader(QtWidgets.QMainWindow):

    # 用于选择文件后发送路径到cw中
    sig = Signal(str)

    def __init__(self):
        # 调用父类的构造函数
        super().__init__()
        self.init_ui()

    # 初始化页面
    def init_ui(self):
        self.setWindowTitle("GP1.5固件升级工具")

        cw = CenterWidget()
        self.setCentralWidget(cw)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(cw)
        scroll.setWidgetResizable(True)

        menu = self.menuBar()
        file_menu = menu.addMenu("开始")
        file_menu.addAction("选择固件路径", self.on_click)

        self.setGeometry(400, 200, 800, 400)

        self.setCentralWidget(scroll)

        # 连接槽函数
        self.sig.connect(cw.on_path_update)

        self.show()

    def on_click(self):
        # 弹出文件选择器
        fd = QtWidgets.QFileDialog()
        fd.setFileMode(QtWidgets.QFileDialog.Directory)
        fd.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        if fd.exec():
            f = fd.selectedFiles()
            # 发送文件路径
            self.sig.emit(f[0])


def main():
    # 获取当前运行脚本所在的包的名称
    app_module = sys.modules["__main__"].__package__

    # 从指定包中获取元数据
    metadata = importlib_metadata.metadata(app_module)

    # 将元数据中Formal-Name字段作为应用程序的名称
    QtWidgets.QApplication.setApplicationName(metadata["Formal-Name"])

    app = QtWidgets.QApplication(sys.argv)
    main_window = FwUpgrader()

    sys.exit(app.exec())
