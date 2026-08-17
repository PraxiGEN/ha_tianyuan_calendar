"""TianYuan (天元历法) 日历平台."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import TianYuanConfigEntry
from .entity import TianYuanBaseEntity
from .coordinator import TianYuanCoordinator

@dataclass(frozen=True, kw_only=True)
class TianYuanCalendarEntityDescription(CalendarEntityDescription):
    """扩展描述符：增加 cal_type 字段用于逻辑分发."""
    cal_type: str 

TIANYUAN_CALENDAR_ENTITIES: tuple[TianYuanCalendarEntityDescription, ...] = (
    TianYuanCalendarEntityDescription(
        key="lunar_almanac",
        translation_key="lunar_almanac",
        icon="mdi:calendar-text",
        cal_type="almanac",
    ),
    TianYuanCalendarEntityDescription(
        key="birthday_reminder",
        translation_key="birthday_reminder",
        icon="mdi:cake-variant",
        cal_type="birthday",
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置日历实体平台."""
    coordinator = entry.runtime_data
    
    async_add_entities([
        TianYuanCalendarEntity(coordinator, entry, description)
        for description in TIANYUAN_CALENDAR_ENTITIES
    ])

class TianYuanCalendarEntity(TianYuanBaseEntity, CalendarEntity):
    """天元通用日历实体类."""

    entity_description: TianYuanCalendarEntityDescription

    def __init__(self, coordinator: TianYuanCoordinator, entry: TianYuanConfigEntry, description: TianYuanCalendarEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    def _get_target_date(self):
        """获取参考日期."""
        return self.coordinator.查看日期 or dt_util.now().date()

    @property
    def event(self) -> CalendarEvent | None:
        """根据类型动态分发今日摘要逻辑."""
        data = self.coordinator.data
        if not data:
            return None

        # 根据描述符中的 cal_type 决定调用哪个方法
        cal_type = self.entity_description.cal_type
        
        if cal_type == "almanac":
            if "全量属性数据" not in data: return None
            事件字典 = self.coordinator._构建单日历事件数据类(data, self._get_target_date())
        else:
            # 生日逻辑
            事件字典 = self.coordinator._构建单生日日历事件数据类(data, self._get_target_date())
        
        return CalendarEvent(**事件字典) if 事件字典 else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """根据类型动态分发范围查询逻辑."""
        cal_type = self.entity_description.cal_type
        
        if cal_type == "almanac":
            return await self.coordinator.获取日历事件范围数据类(
                start_date.date(), 
                end_date.date()
            )
        else:
            # 生日逻辑
            return await self.coordinator.获取生日日历事件范围类(
                start_date.date(), 
                end_date.date()
            )