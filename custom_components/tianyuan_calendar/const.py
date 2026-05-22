"""Constants for the TianYuan (天元农历) integration."""
from __future__ import annotations

import logging
from typing import Final
from homeassistant.const import Platform

# 核心集成元数据
DOMAIN: Final = "tianyuan_calendar"
LOGGER = logging.getLogger(__package__)

# 支持的平台 (整合 SENSOR, SELECT, BUTTON, DATE)
PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.DATE,
]

# 配置键名 (用于 Config Flow 和 Options Flow)
CONF_REFRESH_INTERVAL: Final = "refresh_interval"
CONF_CUSTOM_LONGITUDE: Final = "custom_longitude"
CONF_ENABLE_MORE: Final = "enable_more"
CONF_CALC_MODE: Final = "calc_mode"

# 重试延迟策略表
RETRY_DELAY_MAP = [153, 31, 139, 132, 247, 66, 59, 185, 254, 140, 9, 116, 109, 223, 123, 49, 170, 161, 88, 75, 181, 58, 86, 97, 211, 138, 202, 189, 108, 205, 129, 236, 206, 245, 45, 18, 54, 100, 89, 249, 145, 43, 172, 73, 215, 56, 234, 19, 29, 227, 16, 41, 251, 155, 219, 222, 232, 166, 85, 167, 12, 177, 149, 114, 171, 217, 216, 192, 226, 127, 160, 106, 218, 197, 159, 110, 143, 248, 101, 207, 184, 83, 104, 17, 135, 36, 8, 37, 42, 233, 23, 203, 122, 13, 165, 118, 146, 90, 125, 117, 77, 163, 28, 201, 22, 113, 80, 235, 21, 15, 199, 5, 187, 65, 94, 173, 38, 194, 55, 250, 68, 98, 87, 64, 204, 147, 148, 178, 119, 244, 50, 151, 74, 99, 82, 67, 224, 182, 47, 188, 79, 35, 96, 243, 30, 179, 241, 124, 33, 46, 157, 193, 39, 214, 0, 84, 209, 126, 150, 10, 252, 76, 7, 133, 62, 40, 6, 136, 105, 44, 53, 230, 255, 164, 221, 107, 190, 240, 225, 120, 95, 229, 4, 239, 180, 92, 253, 1, 137, 103, 27, 91, 61, 208, 142, 115, 242, 57, 20, 169, 128, 198, 176, 152, 237, 220, 72, 162, 144, 63, 191, 246, 51, 32, 141, 78, 134, 231, 168, 158, 34, 130, 186, 25, 175, 156, 112, 131, 11, 174, 81, 93, 60, 183, 200, 228, 52, 238, 102, 213, 121, 210, 48, 26, 195, 3, 212, 69, 24, 70, 14, 196, 111, 71, 2, 154]

# 天元术数总开关
CONF_ENABLE_SHUSHU: Final = "enable_shushu"  # 统一开关：启用术数模式

# 计算基准模式
MODE_ST: Final = "standard"  # 标准模式：基于系统时间
MODE_TST: Final = "pro"      # 专业模式：基于真太阳时 (True Solar Time)

# 术数/中医内部数据标识符
TCM_LINGGUI: Final = "linggui"
TCM_NAJIA: Final = "najia"
TCM_NAZI: Final = "nazi"

# 易经卦象内部数据标识符
SHUSHU_HUANGJI_GUA: Final = "huangji_gua"    # 皇极经世值年卦
SHUSHU_MEIHUA_GUA: Final = "meihua_gua"    # 梅花易数时卦

# 协调器内部数据字典键名
KEY_SHUSHU_DATA: Final = "shushu_data" # 存放易经相关数据的 Key

# 术数实体列表 (方便在 sensor.py 中循环注册实体)
SHUSHU_METHODS: Final = [
    TCM_LINGGUI,
    TCM_NAJIA,
    TCM_NAZI,
    SHUSHU_HUANGJI_GUA,
    SHUSHU_MEIHUA_GUA,
]

# 默认值
DEFAULT_REFRESH_INTERVAL: Final = 1  # 默认刷新频率 (分钟)
