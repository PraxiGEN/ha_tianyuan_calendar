"""TianYuan 文本/按钮/日期平台测试（纯逻辑）。"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock

from custom_components.tianyuan_calendar.text import (
    TianYuanTextEntityDescription,
    TianYuanLiuYaoInput,
)
from custom_components.tianyuan_calendar.button import (
    TIANYUAN_BUTTONS,
    TianYuanTodayButton,
)
from custom_components.tianyuan_calendar.date import (
    TIANYUAN_DATE_ENTITIES,
    TianYuanDateNavigator,
)
from .helpers import make_coordinator, make_entry


def test_text_native_value_and_attrs() -> None:
    co = make_coordinator()
    e = TianYuanLiuYaoInput(
        co,
        make_entry(),
        TianYuanTextEntityDescription(
            key="liuyaozhanbu_input",
            translation_key="liuyaozhanbu_input",
            is_private=True,
        ),
    )
    assert e.native_value == "阳阳阳阴阴阴"
    assert "输入规则" in e.extra_state_attributes


async def test_text_set_value() -> None:
    co = make_coordinator()
    co.写入六爻输入类 = AsyncMock()
    e = TianYuanLiuYaoInput(
        co,
        make_entry(),
        TianYuanTextEntityDescription(
            key="liuyaozhanbu_input",
            translation_key="liuyaozhanbu_input",
            is_private=True,
        ),
    )
    await e.async_set_value("111000")
    co.写入六爻输入类.assert_awaited_with("111000")


async def test_button_press_resets_and_refreshes() -> None:
    co = make_coordinator()
    co.async_refresh = AsyncMock()
    e = TianYuanTodayButton(co, make_entry(), TIANYUAN_BUTTONS[0])
    await e.async_press()
    assert co.查看日期 is None
    co.async_refresh.assert_awaited()


def test_date_native_value_default_today() -> None:
    co = make_coordinator()
    e = TianYuanDateNavigator(co, make_entry(), TIANYUAN_DATE_ENTITIES[0])
    assert e.native_value == date.today()


def test_date_native_value_custom() -> None:
    d = date(2026, 1, 1)
    co = make_coordinator(查看日期=d)
    e = TianYuanDateNavigator(co, make_entry(), TIANYUAN_DATE_ENTITIES[0])
    assert e.native_value == d


async def test_date_set_value() -> None:
    co = make_coordinator()
    co.async_refresh = AsyncMock()
    e = TianYuanDateNavigator(co, make_entry(), TIANYUAN_DATE_ENTITIES[0])
    d = date(2026, 5, 5)
    await e.async_set_value(d)
    assert co.查看日期 == d
    co.async_refresh.assert_awaited()
