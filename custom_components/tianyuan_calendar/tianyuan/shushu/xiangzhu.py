"""天元术数引擎 - 易经详注."""
from __future__ import annotations

from typing import Any
from ..library import 获取所有卦名列表类, 获取单卦详注类

class 易经详注类:
    """负责单卦的高级详注提取."""

    @staticmethod
    def 获取易经卦象所有卦名类() -> list[str]:
        """获取所有卦名（供 Select 实体选项使用）"""
        return 获取所有卦名列表类()

    @classmethod
    def 获取易经卦象类(cls, 卦名: str) -> dict[str, Any]:
        """按卦名单独提取原始详注字典"""
        # 增加基础容错：如果卦名为 None 或 "未知"，返回空字典
        if not 卦名 or 卦名 == "未知":
            return {}
        return 获取单卦详注类(卦名)

    @classmethod
    def 获取详注包装类(cls, 卦名: str) -> dict[str, Any]:

        显示卦名 = 卦名 if 卦名 and 卦名 != "未知" else "乾为天"
        卦详细资料 = cls.获取易经卦象类(显示卦名)
        
        return {
            "state": 显示卦名,
            "attributes": 卦详细资料  
        }