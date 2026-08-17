"""TianYuan 选择器平台测试（纯逻辑）。"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from custom_components.tianyuan_calendar.select import (
    TianYuanSelectDescription,
    TianYuanQihuangSelect,
    TianYuanShushuSelect,
    SELECT_TYPE_GENDER,
    SELECT_TYPE_ICHING,
    OPTION_ICHING_SYNC,
)
from custom_components.tianyuan_calendar.tianyuan import (
    辅行诀脏腑用药法要类,
    伤寒杂病论类,
    易经详注类,
)
from .helpers import make_coordinator, make_entry


def _sdesc(key: str, data_type: str, **kw) -> TianYuanSelectDescription:
    return TianYuanSelectDescription(key=key, translation_key=key, data_type=data_type, **kw)


def test_gender_options_fixed() -> None:
    co = make_coordinator()
    e = TianYuanQihuangSelect(co, make_entry(), _sdesc("gender", SELECT_TYPE_GENDER))
    assert e.options == ["male", "female"]


def test_gender_current_option_mapping() -> None:
    co = make_coordinator(性别="女")
    e = TianYuanQihuangSelect(co, make_entry(), _sdesc("gender", SELECT_TYPE_GENDER))
    assert e.current_option == "female"


async def test_gender_select_writes_internal_and_refreshes() -> None:
    co = make_coordinator()
    co.async_refresh = AsyncMock()
    e = TianYuanQihuangSelect(co, make_entry(), _sdesc("gender", SELECT_TYPE_GENDER))
    await e.async_select_option("female")
    assert co.性别 == "女"
    co.async_refresh.assert_awaited()


def test_fuxingjue_current_option_fallback_when_invalid() -> None:
    co = make_coordinator(辅行诀选中大类="不存在的大类")
    with patch.object(辅行诀脏腑用药法要类, "获取所有大类法", return_value=["肝", "心"]):
        e = TianYuanQihuangSelect(co, make_entry(), _sdesc("fuxingjue_viscera", "fuxingjue_viscera"))
        assert e.options == ["肝", "心"]
        # 防御逻辑：当前值不在选项中时回落到第一个选项
        assert e.current_option == "肝"


def test_fuxingjue_options_cascade_symptom() -> None:
    co = make_coordinator(辅行诀选中大类="肝", 辅行诀选中症状="胁下痛")
    with patch.object(辅行诀脏腑用药法要类, "获取大类症状法", return_value=["胁下痛", "目痛"]):
        e = TianYuanQihuangSelect(co, make_entry(), _sdesc("symptom_selector", "symptom"))
        assert e.options == ["胁下痛", "目痛"]


def test_shanghan_options_cascade() -> None:
    co = make_coordinator(伤寒选中六经="太阳", 伤寒选中证型="太阳-表寒实", 伤寒选中方名="麻黄汤")
    with patch.object(伤寒杂病论类, "获取所有六经法", return_value=["太阳", "阳明"]), \
         patch.object(伤寒杂病论类, "获取经下所有证型法", return_value=["太阳-表寒实"]), \
         patch.object(伤寒杂病论类, "获取证型下所有方名法", return_value=["麻黄汤"]):
        e1 = TianYuanQihuangSelect(co, make_entry(), _sdesc("shanghan_channel", "shanghan_channel"))
        assert e1.options == ["太阳", "阳明"]
        e2 = TianYuanQihuangSelect(co, make_entry(), _sdesc("shanghan_syndrome_selector", "shanghan_syndrome"))
        assert e2.options == ["太阳-表寒实"]
        e3 = TianYuanQihuangSelect(co, make_entry(), _sdesc("shanghan_formula_selector", "shanghan_formula"))
        assert e3.options == ["麻黄汤"]


def test_iching_select_options_includes_sync() -> None:
    co = make_coordinator(选中卦名=None)
    with patch.object(易经详注类, "获取易经卦象所有卦名类", return_value=["乾为天", "坤为地"]):
        e = TianYuanShushuSelect(co, make_entry(), _sdesc("iching_selector", SELECT_TYPE_ICHING))
        assert e.options == [OPTION_ICHING_SYNC, "乾为天", "坤为地"]
        assert e.current_option == OPTION_ICHING_SYNC
