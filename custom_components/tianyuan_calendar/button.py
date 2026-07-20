"""TianYuan 按钮平台."""
from __future__ import annotations

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .entity import TianYuanBaseEntity
from .const import DOMAIN

TIANYUAN_BUTTONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="reset_to_today",
        name="Reset to Today",
        translation_key="reset_to_today",
        icon="mdi:calendar-today",
        entity_category=EntityCategory.CONFIG,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """基于 runtime_data 设置按钮实体."""
    coordinator = entry.runtime_data
    entities = [
        TianYuanTodayButton(coordinator, entry, description)
        for description in TIANYUAN_BUTTONS
    ]

    async_add_entities(entities)

class TianYuanTodayButton(TianYuanBaseEntity, ButtonEntity):
    """重置日期到当前的按钮."""

    entity_description: ButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: TianYuanConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    async def async_press(self) -> None:
        """按下按钮."""
        self.coordinator.查看日期 = None
        await self.coordinator.async_refresh()
