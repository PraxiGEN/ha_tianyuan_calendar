"""TianYuan 传感器平台"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import TianYuanConfigEntry
from .tianyuan.maps_loader import 检查专业权限类
from .entity import TianYuanBaseEntity, TianYuanQihuangBaseEntity, TianYuanShushuBaseEntity
from .const import CONF_SYS_TOKEN

@dataclass(frozen=True, kw_only=True)
class TianYuanSensorEntityDescription(SensorEntityDescription):
    """扩展描述符，用于指定协调器中的数据键名."""
    data_key: str | None = None
    is_private: bool = False

# 基础实体
DEFAULT_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="main_lunar",
        name="Lunar Calendar",
        translation_key="main_lunar",
        icon="mdi:calendar",
    ),
    TianYuanSensorEntityDescription(
        key="holiday",
        name="Holiday",
        translation_key="holiday",
        icon="mdi:calendar-star",
        data_key="假期数据",
    ),
    TianYuanSensorEntityDescription(
        key="solar_term",
        name="Solar Term",
        translation_key="solar_term",
        icon="mdi:leaf",
        data_key="节气数据",
    ),
    TianYuanSensorEntityDescription(
        key="shier_shichen",
        name="Shi Er Shi Chen",
        translation_key="shier_shichen",
        icon="mdi:clock-outline",
        data_key="十二时辰数据",
    ),
)

# 更多实体
MORE_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="tst_time",
        name="True Solar Time",
        translation_key="tst_time",
        icon="mdi:sun-clock",
        data_key="真太阳时数据"
    ),
    TianYuanSensorEntityDescription(
        key="sizhu_bazi",
        name="Si Zhu Ba Zi",
        translation_key="sizhu_bazi",
        icon="mdi:dna",
        data_key="四柱八字数据"
    ),
    TianYuanSensorEntityDescription(
        key="tiangan_dizhi",
        name="Tian Gan Di Zhi",
        translation_key="tiangan_dizhi",
        icon="mdi:format-list-bulleted-type",
        data_key="天干地支数据"
    ),
    TianYuanSensorEntityDescription(
        key="shier_tianshen",
        name="Shi Er Tian Shen",
        translation_key="shier_tianshen",
        icon="mdi:shield-star",
        data_key="十二天神数据"
    ),
    TianYuanSensorEntityDescription(
        key="chong_sha",
        name="Chong Sha",
        translation_key="chong_sha",
        icon="mdi:sword-cross",
        data_key="当日冲煞数据"
    ),
    TianYuanSensorEntityDescription(
        key="dongfang_xingxiu",
        name="Dong Fang Xing Xiu",
        translation_key="dongfang_xingxiu",
        icon="mdi:star-shooting",
        data_key="东方星宿数据"
    ),
)

# 岐黄实体
QIHUANG_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="linggui_bafa",
        name="Ling Gui Ba Fa",
        translation_key="linggui_bafa",
        icon="mdi:turtle",
        data_key="灵龟八法数据",
    ),
    TianYuanSensorEntityDescription(
        key="najia_shifa",
        name="Na Jia Shi Fa",
        translation_key="najia_shifa",
        icon="mdi:needle",
        data_key="纳甲筮法数据",
    ),
    TianYuanSensorEntityDescription(
        key="nazi_shifa",
        name="Na Zi Shi Fa",
        translation_key="nazi_shifa",
        icon="mdi:clock-time-four",
        data_key="纳子筮法数据",
    ),
    TianYuanSensorEntityDescription(
        key="feiteng_bafa", 
        name="Fei Teng Ba Fa",
        translation_key="feiteng_bafa", 
        icon="mdi:bird", 
        data_key="飞腾八法数据"
    ),
    TianYuanSensorEntityDescription(
        key="yingsui_buxie",
        name="Ying Sui Bu Xie",
        translation_key="yingsui_buxie",
        icon="mdi:swap-vertical", 
        data_key="迎随补泻数据"
    ),
    # TianYuanSensorEntityDescription(
    #     key="niandu_wuyun", 
    #     name="Nian Du Wu Yun",
    #     translation_key="niandu_wuyun", 
    #     icon="mdi:circle-multiple-outline", 
    #     data_key="年度五运数据"
    # ),
    # TianYuanSensorEntityDescription(
    #     key="niandu_liuqi",
    #     name="Nian Du Liu Qi",
    #     translation_key="niandu_liuqi", 
    #     icon="mdi:weather-windy", 
    #     data_key="年度六气数据"
    # ),
    TianYuanSensorEntityDescription(
        key="liubu_qiji", 
        name="Liu Bu Qi Ji",
        translation_key="liubu_qiji", 
        icon="mdi:step-forward", 
        data_key="六步气机数据"
    ),
    TianYuanSensorEntityDescription(
        key="niandu_yunqi_zonglan",
        name="Nian Du Yun Qi Zong Lan",
        translation_key="niandu_yunqi_zonglan",
        icon="mdi:book-open-page-variant", 
        data_key="年度运气总览数据"
    ),
    TianYuanSensorEntityDescription(
        key="fuxingjue_zangfu_yongyaofa",
        name="Fu Xing Jue Zang Fu Yong Yao Fa",
        translation_key="fuxingjue_zangfu_yongyaofa",
        icon="mdi:medical-bag",
        data_key="辅行诀结果数据",
        is_private=True,
    ),
    # 伤寒杂病论建议
    TianYuanSensorEntityDescription(
        key="shanghan_zabinglun",
        name="Shang Han Za Bing Lun",
        translation_key="shanghan_zabinglun",
        icon="mdi:book-cross",
        data_key="伤寒结果数据",
        is_private=True,
    ),
)

# 术数实体
SHUSHU_SENSORS: tuple[TianYuanSensorEntityDescription, ...] = (
    TianYuanSensorEntityDescription(
        key="xiao_liuren",
        name="Xiao Liu Ren",
        translation_key="xiao_liuren",
        icon="mdi:hand-back-right",
        data_key="小六壬数据",
    ),
    TianYuanSensorEntityDescription(
        key="huangji_jingshi",
        name="Huang Ji Jing Shi",
        translation_key="huangji_jingshi",
        icon="mdi:script-text-outline",
        data_key="皇极经世数据",
    ),
    TianYuanSensorEntityDescription(
        key="meihua_yishu",
        name="Mei Hua Yi Shu",
        translation_key="meihua_yishu",
        icon="mdi:yin-yang",
        data_key="梅花易数数据",
    ),
    TianYuanSensorEntityDescription(
        key="iching_reader",
        name="I Ching Hexagram",
        translation_key="iching_reader",
        icon="mdi:book-open-variant",
        data_key="易经信息数据",
    ),
    TianYuanSensorEntityDescription(
        key="liuyao_shifa",
        name="Liu Yao Shi Fa",
        translation_key="liuyao_shifa",
        icon="mdi:podium-gold",
        data_key="六爻筮法数据",
        is_private=True,
    ),
)

# 注册实体
async def async_setup_entry(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:

    coordinator = entry.runtime_data
    conf = {**entry.data, **entry.options}
    has_pro_access = 检查专业权限类(conf.get(CONF_SYS_TOKEN, ""))
    entities = []

    # 基础实体
    for description in DEFAULT_SENSORS:
        entities.append(TianYuanGenericSensor(coordinator, entry, description))

    # 更多实体
    if conf.get("enable_more"):
        for description in MORE_SENSORS:
            entities.append(TianYuanAdvancedSensor(coordinator, entry, description))

    # 岐黄实体
    if conf.get("enable_qihuang"):
        for desc in QIHUANG_SENSORS:
            if desc.is_private and not has_pro_access:
                continue 
            entities.append(TianYuanQihuangSensor(coordinator, entry, desc))

    # 术数实体
    if conf.get("enable_shushu"):
        for desc in SHUSHU_SENSORS:
            if desc.is_private and not has_pro_access:
                continue 
            entities.append(TianYuanShushuSensor(coordinator, entry, desc))

    async_add_entities(entities)

# 基类
class TianYuanSensorBase(TianYuanBaseEntity, SensorEntity):
    """传感器基类."""

    entity_description: TianYuanSensorEntityDescription

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = description.translation_key

# 默认实体
class TianYuanGenericSensor(TianYuanSensorBase):
    """处理默认核心实体."""

    @property
    def native_value(self) -> StateType:
        key = self.entity_description.key

        if key == "main_lunar":
            l = self.coordinator.data["农历"]
            return f"{l.getMonthInChinese()}月{l.getDayInChinese()}"

        data_key = self.entity_description.data_key
        res = self.coordinator.data.get(data_key)
        return res.get("state") if res else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        key = self.entity_description.key

        if key == "main_lunar":
            return self.coordinator.data.get("全量属性数据", {})

        if key == "shier_shichen":
            return self.coordinator.data.get("十二时辰数据", {}).get("attributes", {})

        return self.coordinator.data.get(self.entity_description.data_key, {})

# 更多实体
class TianYuanAdvancedSensor(TianYuanSensorBase):
    """高级扩展传感器."""

    @property
    def native_value(self) -> StateType:
        # 直接通过 data_key 获取协调器里的中文键对应数据
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("state") if raw else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("attributes", {}) if raw else {}

# 岐黄传感器类
class TianYuanQihuangSensor(TianYuanQihuangBaseEntity, TianYuanSensorBase):
    """岐黄设备专用"""
    @property
    def native_value(self) -> StateType:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("state") if raw else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("attributes", {}) if raw else {}

# 术数实体类
class TianYuanShushuSensor(TianYuanShushuBaseEntity, TianYuanSensorBase):
    """术数设备专用"""
    @property
    def native_value(self) -> StateType:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("state") if raw else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        raw = self.coordinator.data.get(self.entity_description.data_key)
        return raw.get("attributes", {}) if raw else {}