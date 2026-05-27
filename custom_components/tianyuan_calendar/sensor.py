"""TianYuan (天元农历) 传感器平台"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import TianYuanConfigEntry
from .const import (
    DOMAIN,
    CONF_ENABLE_SHUSHU, 
    CONF_ENABLE_MORE, 
    # 基础
    KEY_MAIN_LUNAR, KEY_HOLIDAY, KEY_SOLAR_TERM, KEY_SHICHEN,
    DATA_KEY_HOLIDAY, DATA_KEY_TERM, DATA_KEY_SHICHEN,
    # 更多
    KEY_TST_TIME, KEY_SIZHUBAZI, KEY_TIANGANDIZHI, KEY_TWELVE_GODS, 
    KEY_CHONGSHA, KEY_DONGFANGXINGXIU, DATA_KEY_MORE,
    # 术数
    SHUSHU_LINGGUIBAFA, SHUSHU_NAJIAFA, SHUSHU_NAZIFA, KEY_XIAOLIUREN,
    SHUSHU_HUANGJI_GUA, SHUSHU_MEIHUA_GUA, KEY_ICHING_READER,
    DATA_KEY_SHUSHU, DATA_KEY_XLR, DATA_KEY_ICHING_INFO, DATA_KEY_ICHING_NAME
)
from .entity import TianYuanBaseEntity, TianYuanShushuBaseEntity

@dataclass(frozen=True, kw_only=True)
class TianYuanSensorEntityDescription(SensorEntityDescription):
    """扩展描述符，用于指定协调器中的数据键名."""
    data_key: str | None = None

# 默认实体描述符
DEFAULT_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key=KEY_MAIN_LUNAR,
        name="Lunar Calendar",
        translation_key=KEY_MAIN_LUNAR,
        icon="mdi:calendar",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_HOLIDAY,
        name="Holiday",
        translation_key=KEY_HOLIDAY,
        icon="mdi:calendar-star",
        data_key=DATA_KEY_HOLIDAY,
    ),
    TianYuanSensorEntityDescription(
        key=KEY_SOLAR_TERM,
        name="Solar Term",
        translation_key=KEY_SOLAR_TERM,
        icon="mdi:leaf",
        data_key=DATA_KEY_TERM,
    ),
    TianYuanSensorEntityDescription(
        key=KEY_SHICHEN,
        name="Twelve Time Periods",
        translation_key=KEY_SHICHEN,
        icon="mdi:clock-outline",
        data_key=DATA_KEY_SHICHEN,
    ),
)

# 更多扩展实体描述符
MORE_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key=KEY_TST_TIME,
        name="True Solar Time",
        translation_key=KEY_TST_TIME,
        icon="mdi:sun-clock",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_SIZHUBAZI,
        name="Four Pillars of Destiny",
        translation_key=KEY_SIZHUBAZI,
        icon="mdi:dna",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_TIANGANDIZHI,
        name="Heavenly Stems & Earthly Branches",
        translation_key=KEY_TIANGANDIZHI,
        icon="mdi:format-list-bulleted-type",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_TWELVE_GODS,
        name="Twelve Gods",
        translation_key=KEY_TWELVE_GODS,
        icon="mdi:shield-star",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_CHONGSHA,
        name="Chong Sha",
        translation_key=KEY_CHONGSHA,
        icon="mdi:sword-cross",
    ),
    TianYuanSensorEntityDescription(
        key=KEY_DONGFANGXINGXIU,
        name="Dong Fang Xing Xiu",
        translation_key=KEY_DONGFANGXINGXIU,
        icon="mdi:star-shooting",
    ),
    # TianYuanSensorEntityDescription(
    #     key="season",
    #     name="Season",
    #     translation_key="season",
    #     icon="mdi:weather-partly-cloudy",
    # ),
)

# 天元术数
SHUSHU_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key=SHUSHU_LINGGUIBAFA,
        name="LingGui Eight Methods",
        translation_key=SHUSHU_LINGGUIBAFA,
        icon="mdi:turtle",
        data_key=SHUSHU_LINGGUIBAFA,
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_NAJIAFA,
        name="NaJia Method",
        translation_key=SHUSHU_NAJIAFA,
        icon="mdi:needle",
        data_key=SHUSHU_NAJIAFA,
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_NAZIFA,
        name="NaZi Method",
        translation_key=SHUSHU_NAZIFA,
        icon="mdi:clock-time-four",
        data_key=SHUSHU_NAZIFA,
    ),
    TianYuanSensorEntityDescription(
        key=KEY_XIAOLIUREN,
        name="Xiao Liu Ren Divination",
        translation_key=KEY_XIAOLIUREN,
        icon="mdi:hand-back-right",
        data_key=DATA_KEY_XLR,
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_HUANGJI_GUA,
        name="HuangJi JingShi Monthly Hexagram",
        translation_key=SHUSHU_HUANGJI_GUA,
        icon="mdi:script-text-outline",
        data_key=DATA_KEY_SHUSHU,
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_MEIHUA_GUA,
        name="Meihua Yishu Hexagram",
        translation_key=SHUSHU_MEIHUA_GUA,
        icon="mdi:yin-yang",
        data_key=DATA_KEY_SHUSHU,
    ),
    TianYuanSensorEntityDescription(
        key=KEY_ICHING_READER,
        name="I Ching Hexagram",
        translation_key=KEY_ICHING_READER,
        icon="mdi:book-open-variant",
        data_key=DATA_KEY_ICHING_INFO,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: TianYuanConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """根据配置动态设置传感器实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options} 
    entities: list[SensorEntity] = []

    # 基础实体
    for description in DEFAULT_SENSORS:
        entities.append(TianYuanGenericSensor(coordinator, entry, description))
    # 更多实体
    if conf.get(CONF_ENABLE_MORE):
        for description in MORE_SENSORS:
            entities.append(TianYuanAdvancedSensor(coordinator, entry, description))
    # 术数实体
    if conf.get(CONF_ENABLE_SHUSHU):
        for description in SHUSHU_SENSORS:
            entities.append(TianYuanShushuSensor(coordinator, entry, description))

    async_add_entities(entities)

class TianYuanSensorBase(TianYuanBaseEntity, SensorEntity):
    """传感器基类."""
    
    entity_description: TianYuanSensorEntityDescription

    def __init__(self, coordinator, entry: TianYuanConfigEntry, description: TianYuanSensorEntityDescription):
       
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True

        self._attr_translation_key = description.translation_key

class TianYuanGenericSensor(TianYuanSensorBase):
    """处理默认核心实体."""
    @property
    def native_value(self) -> StateType:
        if self.entity_description.key == KEY_MAIN_LUNAR:
            l = self.coordinator.data["lunar"]
            return f"{l.getMonthInChinese()}月{l.getDayInChinese()}"
        res = self.coordinator.data.get(self.entity_description.data_key)
        return res.get("state") if res else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.entity_description.key == KEY_MAIN_LUNAR:
            return self.coordinator.data.get("full_attributes", {})
        if self.entity_description.key == KEY_SHICHEN:
            return self.coordinator.data.get(DATA_KEY_SHICHEN, {}).get("data", {})
        return self.coordinator.data.get(self.entity_description.data_key, {})


class TianYuanAdvancedSensor(TianYuanSensorBase):
    """高级扩展传感器."""
    @property
    def native_value(self) -> StateType:
        more_data = self.coordinator.data.get(DATA_KEY_MORE, {})
        sensor_info = more_data.get(self.entity_description.key)
        return sensor_info.get("state") if sensor_info else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        more_data = self.coordinator.data.get(DATA_KEY_MORE, {})
        sensor_info = more_data.get(self.entity_description.key)
        return sensor_info.get("attributes", {}) if sensor_info else {}


class TianYuanShushuSensor(TianYuanShushuBaseEntity, TianYuanSensorBase):
    """术数传感器类."""

    def __init__(self, coordinator, entry: TianYuanConfigEntry, description: TianYuanSensorEntityDescription):
        # 显式初始化传感器基类，确保 unique_id 被创建
        super().__init__(coordinator, entry, description)

    @property
    def native_value(self) -> StateType:
        """获取状态值."""
        # 优先处理“易经详注阅读器” (因为它直接读取协调器当前确定的卦名)
        if self.entity_description.key == KEY_ICHING_READER:
            # 返回协调器中计算好的当前展示卦名（实时或手动选择）
            return self.coordinator.data.get(DATA_KEY_ICHING_NAME)

        # 处理其他需要从 data_key 获取的数据
        raw_data = self.coordinator.data.get(self.entity_description.data_key)
        if not raw_data:
            return None

        # 子午流注类 (najia, nazi, linggui)
        if self.entity_description.key in [SHUSHU_NAJIAFA, SHUSHU_NAZIFA, SHUSHU_LINGGUIBAFA]:
            return raw_data.get("summary")

        # 小六壬类
        if self.entity_description.key == KEY_XIAOLIUREN:
            res = self.coordinator.data.get(DATA_KEY_XLR)
            return res.get("state") if res else None

        # 卦象类 (huangji_gua, meihua_gua)
        # 这些数据嵌套在 shushu_data 字典中
        gua_info = raw_data.get(self.entity_description.key)
        return gua_info.get("state") if gua_info else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """获取扩展属性."""
        # 优先处理“易经详注阅读器”
        if self.entity_description.key == KEY_ICHING_READER:
            # 返回加密库中提取的该卦全量字典信息
            return self.coordinator.data.get(DATA_KEY_ICHING_INFO, {})

        # 处理其他数据
        raw_data = self.coordinator.data.get(self.entity_description.data_key)
        if not raw_data:
            return {}

        # 子午流注类
        if self.entity_description.key in [SHUSHU_NAJIAFA, SHUSHU_NAZIFA, SHUSHU_LINGGUIBAFA]:
            return raw_data

        # 小六壬类
        if self.entity_description.key == KEY_XIAOLIUREN:
            res = self.coordinator.data.get(DATA_KEY_XLR)
            return res.get("attributes", {}) if res else {}

        # 卦象类 (返回内部的 attributes 字典)
        gua_info = raw_data.get(self.entity_description.key)
        return gua_info.get("attributes", {}) if gua_info else {}        
