"""天元术数引擎 - 共享基础数据类."""
from __future__ import annotations

from ..library import 加载全量映射表类

maps = 加载全量映射表类()
术数映射 = maps.get("术数类", {})

class 天元术数类:

    八卦基础属性 = 术数映射.get("八卦基础属性", {})
    爻位 = {tuple(v["爻"]): k for k, v in 八卦基础属性.items()}