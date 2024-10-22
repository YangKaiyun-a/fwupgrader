from PySide6.QtCore import QThread

from src.fwupgrader.Data.DataSet import execute_upgrade_script


class UpgradeThread(QThread):
    def __init__(self, general_data, parent=None):
        super().__init__(parent)
        self.fw = general_data.get_fw()
        self.computer_type = general_data.get_computer_type()

    def run(self):
        execute_upgrade_script(self.fw, self.computer_type)