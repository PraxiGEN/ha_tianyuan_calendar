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
    Platform.CALENDAR,
    Platform.DATE,
    Platform.TEXT,
]

# 配置键名 (用于 Config Flow 和 Options Flow)
CONF_REFRESH_INTERVAL: Final = "refresh_interval"
CONF_CUSTOM_LONGITUDE: Final = "custom_longitude"
CONF_ENABLE_MORE: Final = "enable_more"
CONF_CALC_MODE: Final = "calc_mode"
CONF_SYS_TOKEN: Final = "system_token"

# 重试延迟策略表
RETRY_DELAY_MAP = [57, 32, 25, 245, 222, 241, 63, 10, 1, 125, 191, 137, 203, 117, 128, 34, 213, 133, 153, 235, 223, 101, 42, 71, 73, 236, 67, 126, 252, 160, 180, 209, 90, 248, 14, 36, 103, 158, 216, 166, 7, 230, 105, 19, 238, 200, 111, 217, 195, 187, 95, 120, 219, 121, 239, 3, 115, 97, 150, 207, 159, 76, 226, 80, 164, 108, 20, 141, 176, 48, 110, 171, 151, 177, 182, 29, 109, 167, 112, 92, 147, 100, 2, 93, 55, 22, 186, 127, 18, 38, 229, 16, 211, 169, 70, 227, 189, 136, 89, 75, 40, 243, 232, 82, 246, 8, 107, 26, 233, 157, 35, 234, 129, 124, 79, 21, 65, 249, 198, 39, 178, 181, 53, 49, 193, 74, 88, 78, 84, 91, 142, 52, 77, 185, 24, 206, 56, 69, 139, 140, 145, 68, 174, 143, 173, 154, 131, 148, 94, 179, 59, 199, 64, 135, 132, 155, 17, 228, 119, 144, 102, 81, 244, 83, 99, 45, 9, 194, 50, 224, 208, 11, 156, 30, 205, 122, 255, 210, 31, 218, 231, 250, 47, 175, 5, 212, 237, 130, 118, 204, 60, 242, 161, 254, 61, 98, 196, 87, 13, 149, 4, 190, 251, 15, 202, 215, 43, 163, 54, 27, 6, 66, 221, 184, 240, 183, 113, 104, 152, 225, 192, 106, 168, 62, 201, 44, 96, 146, 0, 37, 247, 86, 214, 188, 165, 12, 116, 33, 23, 197, 253, 123, 72, 172, 134, 58, 114, 85, 28, 138, 41, 51, 46, 170, 162, 220]

# 天元术数总开关
CONF_ENABLE_SHUSHU: Final = "enable_shushu"
CONF_ENABLE_QIHUANG: Final = "enable_qihuang"

# 计算基准模式
MODE_ST: Final = "standard"  # 标准模式：基于系统时间
MODE_TST: Final = "pro"      # 专业模式：基于真太阳时 (True Solar Time)

# --- 选择器内部类型 (data_type) ---
SELECT_TYPE_GENDER = "gender"
SELECT_TYPE_ICHING = "iching"

# --- 特殊选项文本 ---
OPTION_ICHING_SYNC = "real_time_follow"

# 默认值
DEFAULT_REFRESH_INTERVAL: Final = 1  # 默认刷新频率 (分钟)
