"""Constants for the TianYuan (天元农历) integration."""
from __future__ import annotations

import logging
from typing import Final
from homeassistant.const import Platform

# 核心集成元数据
DOMAIN: Final = "tianyuan"
LOGGER = logging.getLogger(__package__)

# 支持的平台
PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
]

# 配置键名 (用于 Config Flow 和 Options Flow)
CONF_REFRESH_INTERVAL: Final = "refresh_interval"
CONF_CUSTOM_LONGITUDE: Final = "custom_longitude"
CONF_ENABLE_TCM: Final = "enable_tcm"
CONF_TCM_METHODS: Final = "tcm_methods"
CONF_ENABLE_MORE: Final = "enable_more"

# 模式选择
CONF_CALC_MODE: Final = "calc_mode"
MODE_ST: Final = "standard"  # 兼容模式
MODE_TST: Final = "pro"      # 专业模式

# 中医计算方法标识符
TCM_LINGGUI = "linggui"
TCM_NAJIA = "najia"
TCM_NAZI = "nazi"

# 具体的“灵龟八法”等文字将移动到 .translations/zh-Hans.json 中。
TCM_METHODS = [
    TCM_LINGGUI,
    TCM_NAJIA,
    TCM_NAZI,
]

# 默认值
DEFAULT_REFRESH_INTERVAL: Final = 1  # 分钟

PLATFORMS = [Platform.SENSOR, Platform.SELECT, Platform.BUTTON, Platform.DATE]
