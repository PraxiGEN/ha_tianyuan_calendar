"""TianYuan (天元农历) 选择器平台."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .entity import TianYuanShushuBaseEntity
from .tianyuanshushu import IchingLibrary
from .const import (
    DOMAIN, 
    CONF_ENABLE_SHUSHU,
    KEY_GENDER,
    KEY_ICHING_SELECTOR,
    SELECT_TYPE_GENDER,
    SELECT_TYPE_ICHING,
    OPTION_ICHING_SYNC
)

@dataclass(frozen=True, kw_only=True)
class TianYuanSelectDescription(SelectEntityDescription):
    """自定义选择器描述符."""
    data_type: str  # 'gender' 或 'iching'

# 定义术数设备下的选择实体
TIANYUAN_SELECT_ENTITIES: tuple[TianYuanSelectDescription, ...] = (
    TianYuanSelectDescription(
        key=KEY_GENDER,
        name="Gender",
        translation_key=KEY_GENDER,
        icon="mdi:gender-male-female",
        entity_category=EntityCategory.CONFIG,
        data_type=SELECT_TYPE_GENDER,
    ),
    TianYuanSelectDescription(
        key=KEY_ICHING_SELECTOR,
        name="I Ching Selector",
        translation_key=KEY_ICHING_SELECTOR,
        icon="mdi:book-open-page-variant",
        entity_category=EntityCategory.CONFIG,
        data_type=SELECT_TYPE_ICHING,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置术数相关的选择实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}

    if conf.get(CONF_ENABLE_SHUSHU):
        entities = [
            TianYuanShushuSelect(coordinator, entry, description)
            for description in TIANYUAN_SELECT_ENTITIES
        ]
        async_add_entities(entities)

class TianYuanShushuSelect(TianYuanShushuBaseEntity, SelectEntity):
    """术数设备通用选择器类."""

    entity_description: TianYuanSelectDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: TianYuanConfigEntry,
        description: TianYuanSelectDescription,
    ) -> None:
        """初始化。"""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

        # 初始化选项
        if description.data_type == SELECT_TYPE_GENDER:
            self._attr_options = ["男", "女"]
        elif description.data_type == SELECT_TYPE_ICHING:
            # 选项包含所有卦名，并在最前面增加“实时随动”选项
            self._attr_options = [OPTION_ICHING_SYNC] + IchingLibrary.get_all_names()

    @property
    def current_option(self) -> str | None:
        """返回当前选中的选项。"""
        if self.entity_description.data_type == SELECT_TYPE_GENDER:
            return self.coordinator.gender
        
        # 对于卦象选择器，如果当前没有手动锁定卦象，则显示“实时随动”
        if self.coordinator.selected_iching is None:
            return OPTION_ICHING_SYNC
        
        return self.coordinator.selected_iching

    async def async_select_option(self, option: str) -> None:
        """处理选择动作。"""
        if self.entity_description.data_type == SELECT_TYPE_GENDER:
            self.coordinator.gender = option
            await self.coordinator.async_refresh()
            
        elif self.entity_description.data_type == SELECT_TYPE_ICHING:
            if option == OPTION_ICHING_SYNC:
                # 设置为 None，告诉协调器进入自动同步模式
                await self.coordinator.async_set_iching_gua(None)
            else:
                # 锁定到用户选择的特定卦象
                await self.coordinator.async_set_iching_gua(option)
