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
    TCM_LINGGUI, 
    TCM_NAJIA, 
    TCM_NAZI,
    SHUSHU_MEIHUA_GUA,
    SHUSHU_HUANGJI_GUA
)
from .entity import TianYuanBaseEntity, TianYuanShushuBaseEntity

@dataclass(frozen=True, kw_only=True)
class TianYuanSensorEntityDescription(SensorEntityDescription):
    """扩展描述符，用于指定协调器中的数据键名."""
    data_key: str | None = None

# 默认实体描述符
DEFAULT_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="main_lunar",
        name="Main Lunar",
        translation_key="main_lunar",
        icon="mdi:calendar",
    ),
    TianYuanSensorEntityDescription(
        key="holiday",
        name="Holiday",
        translation_key="holiday",
        icon="mdi:calendar-star",
        data_key="holiday_data",
    ),
    TianYuanSensorEntityDescription(
        key="solar_term",
        name="Solar Term",
        translation_key="solar_term",
        icon="mdi:leaf",
        data_key="term_data",
    ),
    TianYuanSensorEntityDescription(
        key="shichen",
        name="Shichen",
        translation_key="shichen",
        icon="mdi:clock-outline",
        data_key="shichen_data",
    ),
)

# 更多扩展实体描述符
MORE_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="tst_time",
        name="TST Time",
        translation_key="tst_time",
        icon="mdi:sun-clock",
    ),
    TianYuanSensorEntityDescription(
        key="bazi",
        name="BaZi",
        translation_key="bazi",
        icon="mdi:calendar",
    ),
    TianYuanSensorEntityDescription(
        key="ganzhi",
        name="GanZhi",
        translation_key="ganzhi",
        icon="mdi:format-list-bulleted-type",
    ),
    TianYuanSensorEntityDescription(
        key="twelve_gods",
        name="Twelve Gods",
        translation_key="twelve_gods",
        icon="mdi:shield-star",
    ),
    TianYuanSensorEntityDescription(
        key="chongsha",
        name="ChongSha",
        translation_key="chongsha",
        icon="mdi:sword-cross",
    ),
    TianYuanSensorEntityDescription(
        key="xingxiu",
        name="XingXiu",
        translation_key="xingxiu",
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
        key=TCM_LINGGUI,
        name="LingGui",
        icon="mdi:turtle",
        data_key=TCM_LINGGUI,
    ),
    TianYuanSensorEntityDescription(
        key=TCM_NAJIA,
        name="NaJia",
        icon="mdi:needle",
        data_key=TCM_NAJIA,
    ),
    TianYuanSensorEntityDescription(
        key=TCM_NAZI,
        name="NaZi",
        icon="mdi:clock-time-four",
        data_key=TCM_NAZI,
    ),
    TianYuanSensorEntityDescription(
        key="xiaoliuren",
        name="XiaoLiuRen",
        translation_key="xiaoliuren",
        icon="mdi:hand-back-right",
        data_key="xlr_info",
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_HUANGJI_GUA,
        name="Monthly Hexagram",
        icon="mdi:script-text-outline",
        data_key="shushu_data", 
    ),
    TianYuanSensorEntityDescription(
        key=SHUSHU_MEIHUA_GUA,
        name="Hourly Hexagram",
        icon="mdi:yin-yang",
        data_key="shushu_data",
    ),
    TianYuanSensorEntityDescription(
        key="iching_reader",
        name="I Ching",
        translation_key="iching_reader",
        icon="mdi:book-open-variant",
        data_key="iching_info",
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
        self._attr_translation_key = description.key

class TianYuanGenericSensor(TianYuanSensorBase):
    """处理默认核心实体."""
    @property
    def native_value(self) -> StateType:
        if self.entity_description.key == "main_lunar":
            l = self.coordinator.data["lunar"]
            return f"{l.getMonthInChinese()}月{l.getDayInChinese()}"
        res = self.coordinator.data.get(self.entity_description.data_key)
        return res.get("state") if res else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.entity_description.key == "main_lunar":
            return self.coordinator.data.get("full_attributes", {})
        if self.entity_description.key == "shichen":
            return self.coordinator.data.get("shichen_data", {}).get("data", {})
        return self.coordinator.data.get(self.entity_description.data_key, {})


class TianYuanAdvancedSensor(TianYuanSensorBase):
    """高级扩展传感器."""
    @property
    def native_value(self) -> StateType:
        more_data = self.coordinator.data.get("more_entities_data", {})
        sensor_info = more_data.get(self.entity_description.key)
        return sensor_info.get("state") if sensor_info else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        more_data = self.coordinator.data.get("more_entities_data", {})
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
        if self.entity_description.key == "iching_reader":
            # 返回协调器中计算好的当前展示卦名（实时或手动选择）
            return self.coordinator.data.get("iching_display_name")

        # 处理其他需要从 data_key 获取的数据
        raw_data = self.coordinator.data.get(self.entity_description.data_key)
        if not raw_data:
            return None

        # 子午流注类 (najia, nazi, linggui)
        if self.entity_description.key in [TCM_NAJIA, TCM_NAZI, TCM_LINGGUI]:
            return raw_data.get("summary")

        # 小六壬类
        if self.entity_description.key == "xiaoliuren":
            res = self.coordinator.data.get("xlr_info")
            return res.get("state") if res else None

        # 卦象类 (huangji_gua, meihua_gua)
        # 这些数据嵌套在 shushu_data 字典中
        gua_info = raw_data.get(self.entity_description.key)
        return gua_info.get("state") if gua_info else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """获取扩展属性."""
        # 优先处理“易经详注阅读器”
        if self.entity_description.key == "iching_reader":
            # 返回加密库中提取的该卦全量字典信息
            return self.coordinator.data.get("iching_info", {})

        # 处理其他数据
        raw_data = self.coordinator.data.get(self.entity_description.data_key)
        if not raw_data:
            return {}

        # 子午流注类
        if self.entity_description.key in [TCM_NAJIA, TCM_NAZI, TCM_LINGGUI]:
            return raw_data

        # 小六壬类
        if self.entity_description.key == "xiaoliuren":
            res = self.coordinator.data.get("xlr_info")
            return res.get("attributes", {}) if res else {}

        # 卦象类 (返回内部的 attributes 字典)
        gua_info = raw_data.get(self.entity_description.key)
        return gua_info.get("attributes", {}) if gua_info else {}        
