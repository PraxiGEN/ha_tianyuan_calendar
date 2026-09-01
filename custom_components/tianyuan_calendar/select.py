"""TianYuan 选择器平台."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .entity import TianYuanQihuangBaseEntity, TianYuanShushuBaseEntity
from .coordinator import TianYuanCoordinator
from .tianyuan import 易经详注类, 辅行诀脏腑用药法要类, 伤寒杂病论类
from .tianyuan.library import 检查专业权限类
from .const import (
    DOMAIN,
    CONF_ENABLE_QIHUANG,
    CONF_ENABLE_SHUSHU,
    SELECT_TYPE_GENDER,
    SELECT_TYPE_ICHING,
    OPTION_ICHING_SYNC,
    CONF_SYS_TOKEN,
)

@dataclass(frozen=True, kw_only=True)
class TianYuanSelectDescription(SelectEntityDescription):
    """自定义选择器描述符."""
    data_type: str
    is_private: bool = False

# 性别：UI 选项值(英文) 与 协调器内部值(中文) 的映射
# 协调器内部始终以中文「男/女」存储，避免八字乾造/坤造判定错乱
GENDER_OPTION_TO_INTERNAL: Final = {"male": "男", "female": "女"}
GENDER_INTERNAL_TO_OPTION: Final = {"男": "male", "女": "female"}

# 术数设备选择器 (ShuShu)
SHUSHU_SELECT_ENTITIES: tuple[TianYuanSelectDescription, ...] = (
    TianYuanSelectDescription(
        key="iching_selector",
        translation_key="iching_selector",
        icon="mdi:book-open-page-variant",
        entity_category=EntityCategory.CONFIG,
        data_type=SELECT_TYPE_ICHING,
    ),
)

# 岐黄设备选择器 (QiHuang)
QIHUANG_SELECT_ENTITIES: tuple[TianYuanSelectDescription, ...] = (
    # 性别选择现在归属于岐黄设备 (影响子午流注/灵龟八法)
    TianYuanSelectDescription(
        key="gender",
        translation_key="gender",
        icon="mdi:gender-male-female",
        entity_category=EntityCategory.CONFIG,
        data_type=SELECT_TYPE_GENDER,
    ),
    # 辅行诀级联
    TianYuanSelectDescription(
        key="fuxingjue_viscera",
        translation_key="fuxingjue_viscera",
        icon="mdi:account-heart-outline",
        data_type="fuxingjue_viscera",
        entity_category=EntityCategory.CONFIG,
        is_private=True,
    ),
    TianYuanSelectDescription(
        key="symptom_selector",
        translation_key="symptom_selector",
        icon="mdi:emoticon-sick-outline",
        data_type="symptom",
        entity_category=EntityCategory.CONFIG,
        is_private=True,
    ),
    # 伤寒论级联
    TianYuanSelectDescription(
        key="shanghan_channel",
        translation_key="shanghan_channel",
        icon="mdi:pulse",
        data_type="shanghan_channel",
        entity_category=EntityCategory.CONFIG,
        is_private=True,
    ),
    TianYuanSelectDescription(
        key="shanghan_syndrome_selector",
        translation_key="shanghan_syndrome_selector",
        icon="mdi:thermostat",
        data_type="shanghan_syndrome",
        entity_category=EntityCategory.CONFIG,
        is_private=True,
    ),
    TianYuanSelectDescription(
        key="shanghan_formula_selector",
        translation_key="shanghan_formula_selector",
        icon="mdi:mortar-pestle",
        data_type="shanghan_formula",
        entity_category=EntityCategory.CONFIG,
        is_private=True,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """根据配置动态加载选择器实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}
    has_pro_access = 检查专业权限类(conf.get(CONF_SYS_TOKEN, ""))
    entities = []

    if conf.get(CONF_ENABLE_SHUSHU):
        for description in SHUSHU_SELECT_ENTITIES:
            entities.append(TianYuanShushuSelect(coordinator, entry, description))
        
    if conf.get(CONF_ENABLE_QIHUANG): 
        for description in QIHUANG_SELECT_ENTITIES:
            if description.is_private and not has_pro_access:
                continue
            entities.append(TianYuanQihuangSelect(coordinator, entry, description))

    async_add_entities(entities)

# 术数选择器类 (ShuShu Device)
class TianYuanShushuSelect(TianYuanShushuBaseEntity, SelectEntity):
    """归属于天元术数设备的选择器。"""

    entity_description: TianYuanSelectDescription

    def __init__(self, coordinator: TianYuanCoordinator, entry: TianYuanConfigEntry, description: TianYuanSelectDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key
        
        if description.data_type == SELECT_TYPE_ICHING:
            self._attr_options = [OPTION_ICHING_SYNC] + 易经详注类.获取易经卦象所有卦名类()

    @property
    def current_option(self) -> str | None:
        return self.coordinator.选中卦名 or OPTION_ICHING_SYNC

    async def async_select_option(self, option: str) -> None:
        target = None if option == OPTION_ICHING_SYNC else option
        await self.coordinator.选择实体选卦名类(target)

# 岐黄选择器类 (QiHuang Device)
class TianYuanQihuangSelect(TianYuanQihuangBaseEntity, SelectEntity):
    """归属于天元岐黄设备的选择器，支持动态级联选项。"""

    entity_description: TianYuanSelectDescription

    def __init__(self, coordinator: TianYuanCoordinator, entry: TianYuanConfigEntry, description: TianYuanSelectDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def options(self) -> list[str]:
        """动态返回级联后的选项列表。"""
        dtype = self.entity_description.data_type
        
        # 性别选项是固定的
        if dtype == SELECT_TYPE_GENDER:
            return ["male", "female"]
            
        if dtype == "fuxingjue_viscera":
            return 辅行诀脏腑用药法要类.获取所有大类法()
        if dtype == "symptom":
            return 辅行诀脏腑用药法要类.获取大类症状法(self.coordinator.辅行诀选中大类)
            
        if dtype == "shanghan_channel":
            return 伤寒杂病论类.获取所有六经法()
        if dtype == "shanghan_syndrome":
            return 伤寒杂病论类.获取经下所有证型法(self.coordinator.伤寒选中六经)
        if dtype == "shanghan_formula":
            return 伤寒杂病论类.获取证型下所有方名法(self.coordinator.伤寒选中证型)
            
        return []

    @property
    def current_option(self) -> str | None:
        """从协调器读取当前状态，并增加安全过滤。"""
        dtype = self.entity_description.data_type
        
        if dtype == SELECT_TYPE_GENDER: val = GENDER_INTERNAL_TO_OPTION.get(self.coordinator.性别)
        elif dtype == "fuxingjue_viscera": val = self.coordinator.辅行诀选中大类
        elif dtype == "symptom": val = self.coordinator.辅行诀选中症状
        elif dtype == "shanghan_channel": val = self.coordinator.伤寒选中六经
        elif dtype == "shanghan_syndrome": val = self.coordinator.伤寒选中证型
        elif dtype == "shanghan_formula": val = self.coordinator.伤寒选中方名
        else: return None

        # 防御逻辑
        current_options = self.options
        if val not in current_options:
            return current_options[0] if current_options else None
        
        return val

    async def async_select_option(self, option: str) -> None:
        """分发写入逻辑。"""
        dtype = self.entity_description.data_type
        
        if dtype == SELECT_TYPE_GENDER:
            self.coordinator.性别 = GENDER_OPTION_TO_INTERNAL.get(option, "男")
            await self.coordinator.async_refresh()
        elif dtype == "fuxingjue_viscera":
            await self.coordinator.写入辅行诀大类类(option)
        elif dtype == "symptom":
            await self.coordinator.写入辅行诀症状类(option)
        elif dtype == "shanghan_channel":
            await self.coordinator.写入伤寒六经类(option)
        elif dtype == "shanghan_syndrome":
            await self.coordinator.写入伤寒证型类(option)
        elif dtype == "shanghan_formula":
            await self.coordinator.写入伤寒方名类(option)