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
    CONF_ENABLE_TCM, 
    CONF_ENABLE_MORE, 
    TCM_LINGGUI, 
    TCM_NAJIA, 
    TCM_NAZI
)
from .entity import TianYuanBaseEntity

@dataclass(frozen=True, kw_only=True)
class TianYuanSensorEntityDescription(SensorEntityDescription):
    """扩展描述符，用于指定协调器中的数据键名."""
    data_key: str | None = None

# 1. 默认实体描述符
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

# 2. 中医实体描述符
TCM_SENSORS: dict[str, TianYuanSensorEntityDescription] = {
    TCM_LINGGUI: TianYuanSensorEntityDescription(
        key="linggui",
        name="LingGui",
        translation_key="linggui",
        icon="mdi:turtle",
        data_key="linggui",
    ),
    TCM_NAJIA: TianYuanSensorEntityDescription(
        key="najia",
        name="NaJia",
        translation_key="najia",
        icon="mdi:needle",
        data_key="najia",
    ),
    TCM_NAZI: TianYuanSensorEntityDescription(
        key="nazi",
        name="NaZi",
        translation_key="nazi",
        icon="mdi:clock-time-four",
        data_key="nazi",
    ),
}

# 3. 更多扩展实体描述符
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
    # TianYuanSensorEntityDescription(
    #     key="chongsha",
    #     name="ChongSha",
    #     translation_key="chongsha",
    #     icon="mdi:sword-cross",
    # ),
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

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: TianYuanConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """根据配置动态设置传感器实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}
    entities: list[SensorEntity] = []

    for description in DEFAULT_SENSORS:
        entities.append(TianYuanGenericSensor(coordinator, entry, description))

    if conf.get(CONF_ENABLE_TCM):
        for desc in TCM_SENSORS.values():
            entities.append(TianYuanTCMSensor(coordinator, entry, desc))

    if conf.get(CONF_ENABLE_MORE):
        for description in MORE_SENSORS:
            entities.append(TianYuanAdvancedSensor(coordinator, entry, description))

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

class TianYuanTCMSensor(TianYuanSensorBase):
    """中医子午流注传感器."""
    @property
    def native_value(self) -> str | None:
        res = self.coordinator.data.get(self.entity_description.data_key)
        return res.get("summary") if res else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
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
