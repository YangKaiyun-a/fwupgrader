from PySide6.QtCore import QObject, Signal

from src.fwupgrader.Data.Global import ComponentType, ResultType


class SignalManager(QObject):
    # 固件升级进度
    sigProcessPresent = Signal(int)
    # 固件升级完成
    sigProcessFinish = Signal()
    # 固件升级过程中固件的回复
    sigModuleReply = Signal(bool)
    # 发送固件文件名与其绝对路径
    sigUpdateLowerAddress = Signal(dict)
    # 发送上位机，中位机，QPCR文件路径
    sigUpdateFileAddress = Signal(int, str)
    # 上位机，中位机，QPCR，固件升级结果，参数1：模块，参数2：固件cob_id，参数3：升级结果
    sigExecuteScriptResult = Signal(int, int, ResultType)




signal_manager = SignalManager()
