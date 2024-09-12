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

from centerWidget import centerWidget

# from PySide6.QtWidgets import QMenuBar


class FwUpgrader(QtWidgets.QMainWindow):
    sig = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GP1.5固件升级工具")

        cw = centerWidget()
        self.setCentralWidget(cw)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(cw)
        scroll.setWidgetResizable(True)



        menu = self.menuBar()
        file_menu = menu.addMenu("开始")
        file_menu.addAction("选择固件路径", self.on_click)

        self.setGeometry(400, 200, 800, 400)

        #self.setCentralWidget(cw)

        self.setCentralWidget(scroll)

        self.sig.connect(cw.on_path_update)

        self.show()

    def on_click(self):
        # 弹出文件选择器
        fd = QtWidgets.QFileDialog()
        fd.setFileMode(QtWidgets.QFileDialog.Directory)
        fd.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        if fd.exec():
            f = fd.selectedFiles()
            # print(f)
            self.sig.emit(f[0])


def main():
    # Linux desktop environments use app's .desktop file to integrate the app
    # to their application menus. The .desktop file of this app will include
    # StartupWMClass key, set to app's formal name, which helps associate
    # app's windows to its menu item.
    #
    # For association to work any windows of the app must have WMCLASS
    # property set to match the value set in app's desktop file. For PySide2
    # this is set with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__
    # Retrieve the app's metadata
    metadata = importlib_metadata.metadata(app_module)

    QtWidgets.QApplication.setApplicationName(metadata["Formal-Name"])

    app = QtWidgets.QApplication(sys.argv)
    main_window = FwUpgrader()
    sys.exit(app.exec())
