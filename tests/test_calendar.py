"""TianYuan 日历平台测试（纯逻辑）。"""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import AsyncMock

from homeassistant.components.calendar import CalendarEvent

from custom_components.tianyuan_calendar.calendar import (
    TianYuanCalendarEntityDescription,
    TianYuanCalendarEntity,
)
from .helpers import make_coordinator, make_entry


def _cdesc(key: str, cal_type: str) -> TianYuanCalendarEntityDescription:
    return TianYuanCalendarEntityDescription(key=key, translation_key=key, cal_type=cal_type)


def test_almanac_event_dispatches() -> None:
    co = make_coordinator(data={"全量属性数据": {"x": 1}})
    co._构建单日历事件数据类.return_value = {
        "summary": "黄历",
        "start": date(2026, 8, 16),
        "end": date(2026, 8, 16),
    }
    e = TianYuanCalendarEntity(co, make_entry(), _cdesc("lunar_almanac", "almanac"))
    ev = e.event
    assert isinstance(ev, CalendarEvent)
    assert ev.summary == "黄历"
    co._构建单日历事件数据类.assert_called_once()


def test_almanac_event_none_without_full_data() -> None:
    co = make_coordinator(data={})
    e = TianYuanCalendarEntity(co, make_entry(), _cdesc("lunar_almanac", "almanac"))
    assert e.event is None


def test_birthday_event_dispatches() -> None:
    co = make_coordinator(data={"placeholder": True})
    co._构建单生日日历事件数据类.return_value = {
        "summary": "张三生日",
        "start": date(2026, 8, 16),
        "end": date(2026, 8, 16),
    }
    e = TianYuanCalendarEntity(co, make_entry(), _cdesc("birthday_reminder", "birthday"))
    ev = e.event
    assert isinstance(ev, CalendarEvent)
    assert ev.summary == "张三生日"
    co._构建单生日日历事件数据类.assert_called_once()


async def test_async_get_events_routes_almanac() -> None:
    co = make_coordinator()
    co.获取日历事件范围数据类 = AsyncMock(return_value=[])
    e = TianYuanCalendarEntity(co, make_entry(), _cdesc("lunar_almanac", "almanac"))
    await e.async_get_events(None, datetime(2026, 8, 1), datetime(2026, 8, 31))
    co.获取日历事件范围数据类.assert_awaited()


async def test_async_get_events_routes_birthday() -> None:
    co = make_coordinator()
    co.获取生日日历事件范围类 = AsyncMock(return_value=[])
    e = TianYuanCalendarEntity(co, make_entry(), _cdesc("birthday_reminder", "birthday"))
    await e.async_get_events(None, datetime(2026, 8, 1), datetime(2026, 8, 31))
    co.获取生日日历事件范围类.assert_awaited()
