from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Model.MainWidget import MainWidget
from src.fwupgrader.Model.Upper.UpperWiget import UpperWiget
from src.fwupgrader.Model.Middel.MiddelWiget import MiddelWiget
from src.fwupgrader.Model.Lower.LowerWiget import LowerWidget


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mainStackLayout = None  # 定义一个 QStackedWidget
        self.init()

    def init(self):
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        self.mainStackLayout = QStackedWidget(self)

        main_widget = MainWidget()
        upper_widget = UpperWiget()
        middel_widget = MiddelWiget()
        lower_widget = LowerWidget()

        self.mainStackLayout.addWidget(main_widget)  # 索引 0
        self.mainStackLayout.addWidget(upper_widget)  # 索引 1
        self.mainStackLayout.addWidget(middel_widget)  # 索引 2
        self.mainStackLayout.addWidget(lower_widget)  # 索引 3

        self.mainStackLayout.setCurrentIndex(0)

        signal_manager.sigSwitchPage.connect(self.onSigSwitchPage)

        layout = QVBoxLayout(self)
        layout.addWidget(self.mainStackLayout)
        self.setLayout(layout)

    def onSigSwitchPage(self, index):
        if 0 <= index < self.mainStackLayout.count():
            self.mainStackLayout.setCurrentIndex(index)
