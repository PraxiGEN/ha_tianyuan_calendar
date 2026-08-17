"""TianYuan 传感器平台测试（纯逻辑，基于 mock coordinator）。"""

from __future__ import annotations

from homeassistant.const import EntityCategory

from custom_components.tianyuan_calendar.sensor import (
    TianYuanSensorEntityDescription,
    TianYuanGenericSensor,
    TianYuanAdvancedSensor,
    TianYuanQihuangSensor,
    TianYuanShushuSensor,
)
from .helpers import make_coordinator, make_entry, FakeLunar


def _desc(key: str, data_key: str | None = None, **kw) -> TianYuanSensorEntityDescription:
    return TianYuanSensorEntityDescription(
        key=key, translation_key=key, data_key=data_key, **kw
    )


def test_main_lunar_native_value() -> None:
    co = make_coordinator(data={"农历": FakeLunar("七", "廿三")})
    e = TianYuanGenericSensor(co, make_entry(), _desc("main_lunar"))
    assert e.native_value == "七月廿三"
    assert e.available is True


def test_main_lunar_missing_returns_none() -> None:
    co = make_coordinator(data={})
    e = TianYuanGenericSensor(co, make_entry(), _desc("main_lunar"))
    assert e.native_value is None


def test_generic_data_key_state_and_attrs() -> None:
    co = make_coordinator(data={"节气数据": {"state": "立秋", "attributes": {"a": 1}}})
    e = TianYuanGenericSensor(co, make_entry(), _desc("solar_term", data_key="节气数据"))
    assert e.native_value == "立秋"
    assert e.extra_state_attributes == {"a": 1}


def test_generic_missing_data_key_returns_none() -> None:
    co = make_coordinator(data={})
    e = TianYuanGenericSensor(co, make_entry(), _desc("solar_term", data_key="节气数据"))
    assert e.native_value is None


def test_advanced_sensor_reads_data_key() -> None:
    co = make_coordinator(data={"真太阳时数据": {"state": "12:30", "attributes": {"b": 2}}})
    e = TianYuanAdvancedSensor(
        co,
        make_entry(),
        _desc("tst_time", data_key="真太阳时数据", entity_category=EntityCategory.DIAGNOSTIC),
    )
    assert e.native_value == "12:30"
    assert e.extra_state_attributes == {"b": 2}
    assert e.entity_category is EntityCategory.DIAGNOSTIC


def test_qihuang_sensor_reads_data_key() -> None:
    co = make_coordinator(data={"灵龟八法数据": {"state": "x", "attributes": {}}})
    e = TianYuanQihuangSensor(co, make_entry(), _desc("linggui_bafa", data_key="灵龟八法数据"))
    assert e.native_value == "x"


def test_shushu_sensor_reads_data_key() -> None:
    co = make_coordinator(data={"小六壬数据": {"state": "大安", "attributes": {}}})
    e = TianYuanShushuSensor(co, make_entry(), _desc("xiao_liuren", data_key="小六壬数据"))
    assert e.native_value == "大安"


def test_available_false_when_no_data() -> None:
    co = make_coordinator(data=None)
    e = TianYuanGenericSensor(co, make_entry(), _desc("main_lunar"))
    assert e.available is False
