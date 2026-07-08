"""TianYuan (天元农历) 文本平台"""
from __future__ import annotations

from dataclasses import dataclass
from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TianYuanConfigEntry
from .tianyuan.maps_loader import 检查专业权限类
from .entity import TianYuanShushuBaseEntity
from .const import DOMAIN, CONF_SYS_TOKEN

@dataclass(frozen=True, kw_only=True)
class TianYuanTextEntityDescription(TextEntityDescription):
    """文本实体描述符扩展"""
    # 以后如有需要可以在此扩展
    is_private: bool = False

# 定义描述符列表
TIANYUAN_TEXT_ENTITIES: tuple[TianYuanTextEntityDescription, ...] = (
    TianYuanTextEntityDescription(
        key="liuyaozhanbu_input",
        name="Liu Yao Zhan Bu Text Input",
        translation_key="liuyaozhanbu_input",
        icon="mdi:abacus",
        native_min=6, # 缩短最小长度以便调试
        native_max=40,
        pattern=r"^[01阳阴,\-\s123456]*$",
        is_private=True,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """根据配置设置文本输入实体."""
    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}
    has_pro_access = 检查专业权限类(conf.get(CONF_SYS_TOKEN, ""))

    if not conf.get("enable_shushu"):
        return

    entities = []
    
    for description in TIANYUAN_TEXT_ENTITIES:

        if getattr(description, "is_private", False) and not has_pro_access:
            continue
        
        entities.append(TianYuanLiuYaoInput(coordinator, entry, description))

    if entities:
        async_add_entities(entities)

class TianYuanLiuYaoInput(TianYuanShushuBaseEntity, TextEntity):
    """六爻结果输入框类"""

    entity_description: TianYuanTextEntityDescription

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.translation_key

    @property
    def native_value(self) -> str:
        """从协调器中读取当前存储的字符串"""

        return getattr(self.coordinator, "六爻输入字符串", "阳阳阳阴阴阴")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """在属性中写入详细的输入规则说明"""
        return {
            "输入规则": "由左至右对应【初爻】至【上爻】",
            "符号说明": "数字1或汉字'阳'代表阳爻；数字0或汉字'阴'代表阴爻",
            "动爻说明": "使用减号'-'分隔，后跟动爻位置(1-6)",
            "输入示例": "111000-1 代表初爻发动的本卦；阳阳阳阴阴阴-6 代表上爻变",
            "温馨提示": "支持空格和逗号分隔，系统会自动识别"
        }

    async def async_set_value(self, value: str) -> None:
        """用户在界面输入值后触发"""
        await self.coordinator.写入六爻输入类(value)