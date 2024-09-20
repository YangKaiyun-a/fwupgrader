import json
import os
from enum import Enum
import re

# cob_id, 名称， 前缀
lower_module_datas = [
    (0x09, "扩增冷存", "amplification_cool"),
    (0x07, "扩增DJ1", "amplification_dj1"),
    (0x2E, "扩增DJ1电容", "dj_capacitance_1"),
    (0x05, "提取DJ2", "extract_dj1"),
    (0x2F, "扩增DJ1电容", "dj_capacitance_2"),
    (0x24, "DP1夹爪", "dp1_jaw"),
    (0x23, "DP1龙门架", "dp1_xy"),
    (0x04, "DP8移液器", "dp8"),
    (0x2D, "DP8气压电容检测", "pressure_capacitance"),
    (0x03, "DP8龙门架", "dp8_xy"),
    (0x06, "热封模块", "heat_seal"),
    (0x26, "加热振荡1", "heat_shake_1"),
    (0x27, "加热振荡2", "heat_shake_2"),
    (0x28, "加热振荡3", "heat_shake_3"),
    (0x29, "加热振荡4", "heat_shake_4"),
    (0x2A, "加热振荡5", "heat_shake_5"),
    (0x2B, "磁珠振荡", "heat_shake_6"),
    (0x0A, "开关信号", "switch_signal"),
    (0x0B, "紫外状态灯", "light_status"),
    (0x08, "核酸冷存", "cool_store"),
    (0x0C, "风道气压", "environment_monitor"),
    (0x22, "转运", "transporter"),
    (0x0E, "Q龙门架夹爪", "xz_claw"),
]

# 区分中上位机的枚举类型
class ComputerType(Enum):
    Upper = 1
    Middle = 2
    Lower = 3


# 获取上、中位机版本号
def get_version(computer_type) -> str:
    version_file_path = ""
    current_computer_type = ""
    version = ""

    if computer_type == ComputerType.Upper:
        version_file_path = os.path.expanduser('~/GPplus/bin/config/version')
        current_computer_type = "Upper"
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

# 从文件名 amplification_cool.V01.03.01.1001.bin 中解析出版本号 V01.03.01.1001
def get_version_from_file(file_name) -> str:
    version_string = ""
    match = re.search(r'V\d+\.\d+\.\d+\.\d+', file_name)
    if match:
        version_string = match.group(0)

    return version_string