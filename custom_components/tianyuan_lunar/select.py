"""TianYuan (天元农历) 选择器平台."""
from __future__ import annotations

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .entity import TianYuanBaseEntity
from .const import DOMAIN, CONF_ENABLE_TCM

# 使用 SelectEntityDescription
TIANYUAN_SELECT_ENTITIES: tuple[SelectEntityDescription, ...] = (
    SelectEntityDescription(
        key="gender",
        name="Gender",                 # 英文实体名（用于 entity_id）
        translation_key="gender",      # 翻译键（用于 UI 显示）
        icon="mdi:gender-male-female",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置性别选择实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}

    if conf.get(CONF_ENABLE_TCM):
        entities = [
            TianYuanGenderSelect(coordinator, entry, description)
            for description in TIANYUAN_SELECT_ENTITIES
        ]
        async_add_entities(entities)


class TianYuanGenderSelect(TianYuanBaseEntity, SelectEntity):
    """性别选择实体 (影响灵龟八法等计算)."""

    entity_description: SelectEntityDescription
    _attr_has_entity_name = True
    _attr_options = ["男", "女"]

    def __init__(
        self,
        coordinator,
        entry: TianYuanConfigEntry,
        description: SelectEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def current_option(self) -> str | None:
        """返回当前协调器中存储的性别."""
        return self.coordinator.gender

    async def async_select_option(self, option: str) -> None:
        """处理用户选择性别动作."""
        self.coordinator.gender = option
        await self.coordinator.async_refresh()
