import configparser
import hashlib
import json
import os
import shutil
import re
import threading
from pathlib import Path
import pexpect
import paramiko

from src.fwupgrader.Data.SignalManager import signal_manager
from src.fwupgrader.Data.Global import ComponentType, ResultType, ComponentType_name_map, upper_address, middle_address, \
    qpcr_address


success = False
semaphore = threading.Semaphore(0)

def get_current_version_from_file(component_type) -> str:
    """获取当前版本号"""
    if component_type == ComponentType.Upper:
        return get_upper_current_version()
    elif component_type == ComponentType.Middle:
        return get_middle_current_version()
    elif component_type == ComponentType.QPCR:
        return get_qpcr_current_version()

def get_upper_current_version() -> str:
    """获取上位机当前版本号"""
    version = "获取失败"
    version_file_path = os.path.expanduser(upper_address)

    if not os.path.isfile(version_file_path):
        print(f"上位机当前版本文件未找到：{version_file_path}")
        return version

    try:
        with open(version_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            version_in_json = data.get('version')
            if version_in_json is None:
                raise ValueError(f"上位机当前版本号不存在")
            else:
                return version_in_json
    except (json.JSONDecodeError, ValueError):
        print(f"上位机当前版本号解析失败，请检查文件内容")
        return version
    except Exception as e:
        print(f"上位机当前版本号获取失败：{e}")
        return version

def get_middle_current_version() -> str:
    """获取中位机当前版本号"""
    ssh = None
    version = "获取失败"
    host_name = "10.9.13.135"
    user_name = "hcsci"
    pass_word = "hcsci123456"
    remote_version_file = "/opt/GP/bin/version.ini"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_name, username=user_name, password=pass_word)

        sftp = ssh.open_sftp()
        with sftp.open(remote_version_file, 'r') as file:
            content = file.read().decode('utf-8')
        config = configparser.ConfigParser()
        config.read_string(content)
        version = config.get('GP_Version', 'version', fallback="获取失败")
    except Exception as e:
        print(f"中位机当前版本号获取失败：{e}")
    finally:
        if ssh:
            ssh.close()

    return version

def get_qpcr_current_version() -> str:
    """获取QPCR当前版本号"""
    version = "获取失败"
    return version

def get_new_version_from_file(computer_type, file_name) -> str:
    """从升级文件中获取版本号"""
    version_string = "获取失败"

    if computer_type == ComponentType.QPCR:
        # 在file_name的同级目录中找到version.ini
        version_file_path = os.path.join(os.path.dirname(file_name), 'version.ini')
        if os.path.isfile(version_file_path):
            with open(version_file_path, 'r', encoding='utf-8') as file:
                config = configparser.ConfigParser()
                config.read_file(file)
                try:
                    version_in_file = config.get('QPCR_Version', 'version')
                    if not version_in_file:
                        raise ValueError("QPCR版本号不存在")
                    else:
                        version_string = version_in_file
                except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
                    print("QPCR版本号解析失败，请检查文件内容")
    else:
        match = re.search(r'V\d+\.\d+\.\d+\.\d+', file_name)
        if match:
            version_string = match.group(0)

    return version_string

def parse_upper_update_file(directory):
    """解析上位机升级文件"""
    file_absolute_path = match_file(directory, 'GPplus-V*')
    signal_manager.sigUpdateFileAddress.emit(ComponentType.Upper.value, file_absolute_path)

def parse_middle_update_file(directory):
    """解析中位机升级文件"""
    file_absolute_path = match_file(directory, 'GPinstall-V*')
    signal_manager.sigUpdateFileAddress.emit(ComponentType.Middle.value, file_absolute_path)

def parse_qpcr_update_file(directory):
    """解析QPCR升级文件和版本号"""
    file_absolute_path = match_file(directory, 'qpcr_upgrade.sh')
    signal_manager.sigUpdateFileAddress.emit(ComponentType.QPCR.value, file_absolute_path)

def parse_lower_update_file(directory):
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

def parse_update_file(directory):
    """从路径中解析出升级文件"""
    parse_upper_update_file(directory)
    parse_middle_update_file(directory)
    parse_qpcr_update_file(directory)
    parse_lower_update_file(directory)



"""功能函数"""
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

def match_file(directory, condition) -> str:
    """匹配文件
    参数1：指定路经
    参数2：匹配条件
    返回值：文件的绝对路径
    """
    file = next(Path(directory).rglob(condition))
    file_absolute_path = str(file.resolve())
    return file_absolute_path

if __name__ == "__main__":
    path = os.path.expanduser("~/V01.03.01.1001/GPplus-V01.03.01.1001-d031decd4bcc8b584d9c92eefedd3a44c8d88c41.sh")
    execute_upper_script(path)
