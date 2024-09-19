from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QHBoxLayout, QApplication
)
from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Model.MainWidget import MainWidget
from src.fwupgrader.Model.Upper.UpperWiget import UpperWiget
from src.fwupgrader.Model.Middel.MiddelWiget import MiddelWiget
from src.fwupgrader.Model.Lower.LowerWiget import LowerWidget


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.btnBack = None
        self.content_stack = None
        self.init()

    def init(self):
        self.init_ui()

    # 初始化ui
    def init_ui(self):
        top_widget = QWidget()
        top_widget.setObjectName("top_widget")
        top_widget.setStyleSheet("QWidget#top_widget {border: 1px solid black;}")

        content_widget = QWidget()
        content_widget.setObjectName("content_widget")
        content_widget.setStyleSheet("QWidget#content_widget {border: 1px solid blue;}")

        # 返回按钮
        self.btnBack = QPushButton("返回")
        self.btnBack.setFixedSize(150, 50)
        self.btnBack.clicked.connect(self.onBtnBackClicked)

        # top_widget布局
        top_hlayout = QHBoxLayout(top_widget)
        top_hlayout.addStretch()
        top_hlayout.addWidget(self.btnBack)

        # content_widget布局
        content_hlayout = QHBoxLayout(content_widget)
        self.content_stack = QStackedWidget()
        self.content_stack.currentChanged.connect(self.onCurrentChanged)
        content_hlayout.addWidget(self.content_stack)

        # 主布局
        main_vlayout = QVBoxLayout(self)
        main_vlayout.addWidget(top_widget, stretch=1)
        main_vlayout.addWidget(content_widget, stretch=10)

        main_widget = MainWidget()
        upper_widget = UpperWiget()
        middel_widget = MiddelWiget()
        lower_widget = LowerWidget()

        self.content_stack.addWidget(main_widget)  # 索引 0
        self.content_stack.addWidget(upper_widget)  # 索引 1
        self.content_stack.addWidget(middel_widget)  # 索引 2
        self.content_stack.addWidget(lower_widget)  # 索引 3
        self.content_stack.setCurrentIndex(0)

        # 切换页面信号槽
        signal_manager.sigSwitchPage.connect(self.onSigSwitchPage)

    # 返回按钮槽函数
    def onBtnBackClicked(self):
        current_index = self.content_stack.currentIndex()
        if current_index == 0:
            QApplication.quit()
        else:
            self.content_stack.setCurrentIndex(0)

    def onCurrentChanged(self, index):
        if index == 0:
            self.btnBack.setText("退出")
        else:
            self.btnBack.setText("返回")

    # 切换页面
    def onSigSwitchPage(self, index):
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
