import os

import pexpect
from PySide6.QtCore import QThread, Slot
import threading
import hashlib
from src.fwupgrader.Data.DataSet import backup_current_version, rollback
from src.fwupgrader.Data.Global import ComponentType, ResultType
from src.fwupgrader.Data.SignalManager import signal_manager


class UpgradeThread(QThread):
    def __init__(self, update_components, parent=None):
        super().__init__(parent)
        self.update_components = update_components      # 存储当前需要升级的所有部件
        self.semaphore = threading.Semaphore(0)
        self.success = False
        self.cob_id = None                              # 固件index

    def run(self):
        """执行升级脚本"""
        for component in self.update_components:
            # 这里要区分上位机、中位机、QPCR、固件模块
            directory = component.get_fw()
            component_type = component.get_component_type()

            if component_type == ComponentType.Upper:
                self.execute_upper_script(directory)
            elif component_type == ComponentType.Middle:
                self.execute_middle_script(directory)
            elif component_type == ComponentType.QPCR:
                self.execute_qpcr_script(directory)
            elif component_type == ComponentType.Lower:
                self.execute_lower_update(component)

    def execute_upper_script(self, directory):
        """执行上位机升级脚本"""
        print(f"即将进行上位机升级，升级文件位于：{directory}")

        signal_manager.sigExecuteScriptResult.emit(ComponentType.Upper, 0, ResultType.START)

        backup_path = os.path.expanduser("~/GPplus_backup")
        current_file = os.path.expanduser("~/GPplus")

        # 备份文件
        if not backup_current_version(backup_path, current_file):
            # 备份文件失败后终止升级
            result_message = "备份原始文件失败，终止升级！"
            print(result_message)
            signal_manager.sigExecuteScriptResult.emit(ComponentType.Upper, 0, False)
            return

        print("备份原始文件成功！")

        try:
            # 使用pexpect来模拟用户输入
            child = pexpect.spawn(f'bash {directory}', encoding='utf-8')
            child.expect(r'.*密码.*|.*password.*')
            child.sendline('1')
            child.expect(pexpect.EOF)
            result_message = "上位机升级成功"
            print(result_message)
            signal_manager.sigExecuteScriptResult.emit(ComponentType.Upper, 0, ResultType.SUCCESSED)
        except Exception as e:
            result_message = f"上位机升级失败：{str(e)}，即将回滚到上一个版本"
            print(result_message)
            signal_manager.sigExecuteScriptResult.emit(ComponentType.Upper, 0, ResultType.FAILD)
            rollback(current_file, backup_path)

    def execute_middle_script(self, directory):
        """执行中位机升级脚本"""
        print(f"执行中位机升级脚本：{directory}")

    def execute_qpcr_script(self, directory):
        """执行QPCR升级脚本"""
        print(f"执行QPCR升级脚本：{directory}")

    def execute_lower_update(self, component):
        """执行固件升级脚本"""
        component.set_in_process(True)
        remote = component.get_remote()
        self.cob_id = component.get_cob_id()

        print(f"执行固件：{component.get_component_type_name()}")

        # 读取固件文件，r：只读，b：二进制
        with open(component.get_fw(), "rb") as f:
            fw_data = f.read()

        # 计算固件文件的MD5值
        m = hashlib.md5()
        m.update(fw_data)

        try:
            # 向远程设备发送MD5和大小
            print(f"发送MD5：{m.hexdigest()}")
            remote.sdo["iap"]["md5"].raw = m.digest()
            print(f"发送文件大小：{len(fw_data)} KB")
            remote.sdo["iap"]["size"].raw = len(fw_data)
            self.success = True
        except Exception as e:
            print("参数发送错误")
            self.success = False
            self.cob_id = None

        # 如果参数发送失败，终止升级
        if not self.success:
            signal_manager.sigExecuteScriptResult.emit(ComponentType.Lower, 0, ResultType.FAILD)
            self.cob_id = None
            return

        print("开始发送数据")

        # 分块发送固件数据，每块32字节
        frames = [fw_data[i: i + 32] for i in range(0, len(fw_data), 32)]
        total = len(frames)
        print(f"将文件分为{total}块")

        for idx, f in enumerate(frames):
            try:
                # 设置偏移
                remote.sdo["iap"]["offset"].raw = idx * 32
                print(f"offset: {idx * 32}")
                # 发送数据块
                remote.sdo["iap"]["data"].raw = f
                print(f"data: {f}")
            except Exception as e:
                self.success = False
                self.cob_id = None
            if not self.success:
                break

            # 等待应答信号，应答信号由固件模块类内发出，如果超时则终止
            if not self.semaphore.acquire(timeout=10):
                self.success = False
                self.cob_id = None
                break

        signal_manager.sigExecuteScriptResult.emit(ComponentType.Lower, 0, ResultType.SUCCESSED)

    @Slot(bool)
    def onSigModuleReply(self, cob_id, result):
        """接收固件回复，释放线程信号量"""
        if self.cob_id != cob_id:
            return

        self.success = result
        self.semaphore.release()