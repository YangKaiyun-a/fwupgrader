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

from MainWindow import MainWindow
from Data.SignalManager import SignalManager


def main():
    QtWidgets.QApplication.setApplicationName("GP_UpdateTool")

    # 初始化信号类
    signal_manager = SignalManager()

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec())
