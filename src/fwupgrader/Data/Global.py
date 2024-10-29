from enum import Enum

upper_address = "~/GPplus/bin/config/version"           # 上位机版本号目录
middle_address = "~/GPinstall/bin/config/version"       # 上位机版本号目录
qpcr_address = "~/QPCR/version.ini"                     # 上位机版本号目录

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
    (0x0E, "Q龙门架夹爪", "xz_claw")
]


# 区分中上位机的枚举类型
class ComponentType(Enum):
    Upper = 0
    Middle = 1
    QPCR = 2
    Lower = 3

# 根据部件索引快速访问名称，当前版本，最新版本
ComponentType_name_map = {
    ComponentType.Upper: "上位机",
    ComponentType.Middle: "中位机",
    ComponentType.QPCR: "QPCR"
}

# 升级过程中的返回类型
class ResultType(Enum):
    EMPTY_PATH = 0,         # 升级路径为空
    START = 1,              # 开始升级
    SUCCESSED = 2,          # 升级成功
    FAILD = 3               # 升级失败
