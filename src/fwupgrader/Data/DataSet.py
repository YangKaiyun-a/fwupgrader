import json
import os
import shutil
import re
from pathlib import Path
import pexpect

from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Data.Global import ComputerType

def get_current_version_from_file(computer_type) -> str:
    """获取上、中位机版本号"""
    version_file_path = ""
    current_computer_type = ""
    version = ""

    if computer_type == ComputerType.Upper:
        version_file_path = os.path.expanduser('~/GPplus/bin/config/version')
        current_computer_type = "GeneralData"
    elif computer_type == ComputerType.Middle:
        version_file_path = os.path.expanduser('~/GPplus/bin/config/version')
        current_computer_type = "Middle"

    if not os.path.isfile(version_file_path):
        raise FileNotFoundError(f"{current_computer_type}版本文件未找到，{version_file_path}")

    try:
        with open(version_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            version = data.get('version')

            if version is None:
                raise ValueError(f"{current_computer_type}版本号不存在")
            return version
    except json.JSONDecodeError:
        print(f"{current_computer_type}版本号解析失败，请检查文件内容")
        return version
    except Exception as e:
        print(f"{current_computer_type}获取失败：{e}")
        return version


def get_new_version_from_file(file_name) -> str:
    """从文件名中解析出版本号 V01.03.01.1001"""
    version_string = ""
    match = re.search(r'V\d+\.\d+\.\d+\.\d+', file_name)
    if match:
        version_string = match.group(0)

    return version_string


def match_file(directory, condition) -> str:
    file = next(Path(directory).rglob(condition))
    file_absolute_path = str(file.resolve())

    return file_absolute_path


def match_lower_file(directory):
    """解析固件升级文件"""
    bin_file_dict = {}
    bin_file_list = [file for file in Path(directory).rglob('*.bin')]

    for bin_file in bin_file_list:
        # 文件名（不带后缀.bin）
        file_name_without_extension = bin_file.stem
        # 绝对路径
        file_absolute_path = str(bin_file.resolve())
        # 组合为字典
        bin_file_dict[file_name_without_extension] = file_absolute_path

    signal_manager.sigUpdateLowerAddress.emit(bin_file_dict)


def match_upper_file(directory):
    """解析上位机升级文件"""
    file_absolute_path = match_file(directory, 'GPplus-V*')
    signal_manager.sigUpdateUpperAddress.emit(file_absolute_path)


def match_middle_file(directory):
    """解析中位机升级文件"""
    file_absolute_path = match_file(directory, 'GPinstall-V*')
    signal_manager.sigUpdateMiddleAddress.emit(file_absolute_path)


def parse_update_file(directory):
    """从路径中解析出升级文件"""
    match_upper_file(directory)
    match_middle_file(directory)
    match_lower_file(directory)


def backup_current_version(backup_path, current_version):
    """
    执行文件备份
    参数1: 备份文件的目录
    参数2: 当前文件的目录
    """
    try:
        if Path(backup_path).exists():
            shutil.rmtree(backup_path)
        shutil.copytree(current_version, backup_path)
        return True
    except Exception as e:
        print(f"备份失败：{e}")
        return False


def rollback(current_version_path, backup_path):
    """
    回滚到上一个版本
    参数1: 当前文件目录
    参数2: 备份文件的目录
    """
    print(f"执行回滚操作，将{backup_path}还原到{current_version_path}")

    try:
        if Path(current_version_path).exists():
            shutil.rmtree(current_version_path)  # 删除当前版本
        shutil.copytree(backup_path, current_version_path)  #恢复备份
        print("回滚成功，恢复到上一版本")
    except Exception as e:
        print(f"回滚失败：{str(e)}")


def execute_upper_script(directory):
    """执行上位机升级脚本"""
    print(f"即将进行上位机升级，升级文件位于：{directory}")

    backup_path = os.path.expanduser("~/GPplus_backup")
    current_file = os.path.expanduser("~/GPplus")

    # 备份文件
    if not backup_current_version(backup_path, current_file):
        #备份文件失败后终止升级
        result_message = "备份原始文件失败，终止升级！"
        print(result_message)
        signal_manager.sigExecuteScriptResult.emit(ComputerType.Upper, False)
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
        signal_manager.sigExecuteScriptResult.emit(ComputerType.Upper, True)
    except Exception as e:
        result_message = f"上位机升级失败：{str(e)}，即将回滚到上一个版本"
        print(result_message)
        signal_manager.sigExecuteScriptResult.emit(ComputerType.Upper, False)
        rollback(current_file, backup_path)



def execute_middle_script(directory):
    """执行中位机升级脚本"""
    print(f"执行中位机升级脚本：{directory}")


def execute_upgrade_script(directory, computer_type):
    """执行升级脚本"""
    if computer_type == ComputerType.Upper:
        execute_upper_script(directory)
    # elif computer_type == ComputerType.Middle:
    #     execute_middle_script(directory)


if __name__ == "__main__":
    path = os.path.expanduser("~/V01.03.01.1001/GPplus-V01.03.01.1001-d031decd4bcc8b584d9c92eefedd3a44c8d88c41.sh")
    execute_upper_script(path)
