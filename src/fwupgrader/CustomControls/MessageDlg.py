import sys

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QApplication, QDialog


class MessageDlg(QDialog):
    def __init__(self, message, parent=None):
        super(MessageDlg, self).__init__(parent)

        self.setWindowTitle("Message Dlg")
        self.setGeometry(300, 300, 300, 150)

        layout = QtWidgets.QVBoxLayout()

        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.button = QPushButton("确定", self)
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def setText(self, text):
        self.label.setText(text)

    def setBtnEnabled(self, enable):
        self.button.setEnabled(enable)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MessageDlg("你好")
    dialog.exec()
    sys.exit(app.exec())