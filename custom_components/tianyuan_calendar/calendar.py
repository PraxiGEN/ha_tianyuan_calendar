"""TianYuan 日历平台."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timedelta 
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

@dataclass(frozen=True, kw_only=True)
class TianYuanCalendarEntityDescription(CalendarEntityDescription):
    """天元日历描述符扩展."""

# 定义实体描述符
LUNAR_CALENDAR_DESCRIPTION = TianYuanCalendarEntityDescription(
    key="lunar_almanac",
    translation_key="lunar_almanac",
    icon="mdi:calendar-text", 
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置天元农历日历实体平台."""
    coordinator = entry.runtime_data
    
    # 注册实体
    async_add_entities([
        TianYuanCalendarEntity(coordinator, entry, LUNAR_CALENDAR_DESCRIPTION)
    ])

class TianYuanCalendarEntity(TianYuanBaseEntity, CalendarEntity):
    """天元历书实体."""

    entity_description: TianYuanCalendarEntityDescription

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def event(self) -> CalendarEvent | None:
        """返回当前的日历事件摘要（联动协调器的最新数据与查阅日期）."""
        data = self.coordinator.data
        if not data or "全量属性数据" not in data:
            return None
            
        目标日期 = self.coordinator.查看日期 or dt_util.now().date()
        事件字典 = self.coordinator._构建单日历事件数据类(data, 目标日期)
        
        return CalendarEvent(**事件字典)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """向协调器请求指定范围的事件列表. """
        # 直接调用协调器提供的稳健接口
        return await self.coordinator.获取日历事件范围数据类(
            start_date.date(), 
            end_date.date()
        )
    