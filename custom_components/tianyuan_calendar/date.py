"""TianYuan (天元农历) 日期导航平台."""
from __future__ import annotations
from datetime import date

from homeassistant.components.date import (
    DateEntity,
    DateEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .entity import TianYuanBaseEntity
from .const import DOMAIN, KEY_DATE_NAVIGATOR

# 使用 DateEntityDescription
TIANYUAN_DATE_ENTITIES: tuple[DateEntityDescription, ...] = (
    DateEntityDescription(
        key=KEY_DATE_NAVIGATOR,
        name="Date Navigator",
        translation_key=KEY_DATE_NAVIGATOR,
        icon="mdi:calendar-search",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置日期选择实体."""
    coordinator = entry.runtime_data

    entities = [
        TianYuanDateNavigator(coordinator, entry, description)
        for description in TIANYUAN_DATE_ENTITIES
    ]

    async_add_entities(entities)


class TianYuanDateNavigator(TianYuanBaseEntity, DateEntity):
    """日期导航实体：允许用户在 UI 上直接选择计算基准日."""

    entity_description: DateEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: TianYuanConfigEntry,
        description: DateEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def native_value(self) -> date:
        """返回当前显示的日期."""
        return self.coordinator.view_date or date.today()

    async def async_set_value(self, value: date) -> None:
        """用户在 UI 日历控件选择了新日期."""
        self.coordinator.view_date = value
        await self.coordinator.async_refresh()
