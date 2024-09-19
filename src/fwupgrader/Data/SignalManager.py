from PySide6.QtCore import QObject, Signal


class SignalManager(QObject):
    # 切换页面
    sigSwitchPage = Signal(int)
    # 升级进度
    sigProcessPresent = Signal(int)
    # 升级完成
    sigProcessFinish = Signal()
    # 升级过程中固件的回复
    sigModuleReply = Signal(bool)
    # 发送固件文件名与其绝对路径
    sigUpdateLowerAdress = Signal(dict)


signal_manager = SignalManager()
