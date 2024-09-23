from PySide6.QtCore import QObject, Signal


class SignalManager(QObject):
    # 切换页面
    sigSwitchPage = Signal(int)
    # 固件升级进度
    sigProcessPresent = Signal(int)
    # 固件升级完成
    sigProcessFinish = Signal()
    # 固件升级过程中固件的回复
    sigModuleReply = Signal(bool)
    # 发送固件文件名与其绝对路径
    sigUpdateLowerAddress = Signal(dict)
    # 发送上位机文件路径
    sigUpdateUpperAddress = Signal(str)
    # 发送中位机文件路径
    sigUpdateMiddleAddress = Signal(str)
    # 上中位机升级结果
    sigExecuteScriptResult = Signal(str)




signal_manager = SignalManager()
