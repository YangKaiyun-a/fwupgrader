from PySide6.QtCore import QThread

from src.fwupgrader.Data.DataSet import execute_upgrade_script


class UpgradeThread(QThread):
    def __init__(self, update_components, parent=None):
        super().__init__(parent)
        self.update_components = update_components      # 存储当前需要升级的所有部件

    def run(self):
        execute_upgrade_script(self.update_components)