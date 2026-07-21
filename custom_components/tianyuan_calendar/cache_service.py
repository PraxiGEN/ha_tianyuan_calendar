"""TianYuan 缓存服务"""

import time
import asyncio
import inspect
from collections import OrderedDict, defaultdict
from typing import Any, Callable, Awaitable

class CacheService:
    """工业级缓存服务"""

    def __init__(self, capacity: int = 500):
        self.capacity = capacity
        # key -> (value, timestamp)
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        # key-level lock（防止缓存击穿）
        self._locks = defaultdict(asyncio.Lock)

    def _is_expired(self, ts: float, ttl: int) -> bool:
        return (time.time() - ts) > ttl

    def _evict_if_needed(self):
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)  # LRU

    async def get_or_set(
        self,
        key: str,
        builder: Callable[[], Any | Awaitable[Any]],
        ttl: int = 86400,
    ) -> Any:
        now = time.time()

        # 快速命中
        if key in self._cache:
            value, ts = self._cache[key]
            if not self._is_expired(ts, ttl):
                self._cache.move_to_end(key)  # LRU refresh
                return value
            else:
                del self._cache[key]

        # 防击穿锁
        async with self._locks[key]:
            # Double check
            if key in self._cache:
                value, ts = self._cache[key]
                if not self._is_expired(ts, ttl):
                    return value

            # 执行构建器 (Builder)
            result = builder()
            
            # 这可以准确识别并等待 Coroutine, Task, 以及 hass 返回的 Future 对象
            if inspect.isawaitable(result):
                result = await result

            # 写入缓存
            self._cache[key] = (result, now)
            self._cache.move_to_end(key)
            self._evict_if_needed()

            return result

    def invalidate(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        self._cache.clear()