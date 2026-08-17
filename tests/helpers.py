"""TianYuan 测试辅助：构造轻量 mock coordinator 与 entry。

这些 helper 不依赖真实的 lunar_python / assets.dat，仅用于实体纯逻辑断言，
可在安装了 homeassistant 测试框架（pytest-homeassistant）的环境中运行。
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock


def make_entry(entry_id: str = "test_entry") -> SimpleNamespace:
    """返回最小可用的 entry 替身，仅提供实体构造所需的 entry_id。"""
    return SimpleNamespace(entry_id=entry_id)


class FakeLunar:
    """模拟 lunar_python.Lunar 在 main_lunar 取值时用到的方法。"""

    def __init__(self, month: str = "七", day: str = "廿三") -> None:
        self._month = month
        self._day = day

    def getMonthInChinese(self) -> str:
        return self._month

    def getDayInChinese(self) -> str:
        return self._day


def make_coordinator(data: dict | None = None, **kwargs) -> MagicMock:
    """构造一个 MagicMock 充当 coordinator，提供各实体读取所需的属性。"""
    co = MagicMock()
    co.data = data if data is not None else {}
    co.last_update_success = True
    co.性别 = kwargs.get("性别", "男")
    co.选中卦名 = kwargs.get("选中卦名", None)
    co.辅行诀选中大类 = kwargs.get("辅行诀选中大类", "肝")
    co.辅行诀选中症状 = kwargs.get("辅行诀选中症状", "胁下痛")
    co.伤寒选中六经 = kwargs.get("伤寒选中六经", "太阳")
    co.伤寒选中证型 = kwargs.get("伤寒选中证型", "太阳-表寒实")
    co.伤寒选中方名 = kwargs.get("伤寒选中方名", "麻黄汤")
    co.六爻输入字符串 = kwargs.get("六爻输入字符串", "阳阳阳阴阴阴")
    co.查看日期 = kwargs.get("查看日期", None)
    return co
