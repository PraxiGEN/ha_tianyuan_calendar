"""TianYuan 高级缓存服务 V2"""

import time
import asyncio
import inspect
import logging
from collections import OrderedDict
from typing import Any, Callable, Awaitable, Optional
from .const import LOGGER

class CacheService:
    def __init__(self, capacity: int = 500):
        self.capacity = capacity
        # 结构: key -> (value, expire_at)
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        # 显式管理锁，避免内存泄露
        self._locks: dict[str, asyncio.Lock] = {}

    def _is_expired(self, expire_at: float) -> bool:
        return time.time() > expire_at

    def _evict_logic(self):
        """混合清理策略：优先删除过期项，其次按 LRU 淘汰"""
        now = time.time()
        # 扫描并删除已过期项 (仅扫描部分，避免 O(n) 过大)
        keys_to_del = [k for k, v in self._cache.items() if now > v[1]]
        for k in keys_to_del:
            del self._cache[k]
        
        # 如果依然超量，执行 LRU 淘汰
        while len(self._cache) > self.capacity:
            self._cache.popitem(last=False)

    async def get_or_set(
        self,
        key: str,
        builder: Callable[[], Any | Awaitable[Any]],
        ttl: int = 86400,
        cache_none: bool = True  # 是否允许缓存 None
    ) -> Any:
        # 尝试从缓存中提取 (无锁快速路径)
        if key in self._cache:
            value, expire_at = self._cache[key]
            if not self._is_expired(expire_at):
                self._cache.move_to_end(key)
                return value
            else:
                del self._cache[key]

        # 细粒度锁管理（获取或创建锁）
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
            try:
                # Double Check (二次检查)
                if key in self._cache:
                    value, expire_at = self._cache[key]
                    if not self._is_expired(expire_at):
                        return value

                # 计算数据 (Builder)
                try:
                    result = builder()
                    if inspect.isawaitable(result):
                        result = await result
                except Exception as err:
                    LOGGER.error("缓存构建器在处理该 key 时失败 %s: %s", key, err)
                    raise  # 抛出异常，不写入缓存

                # 判定是否缓存 None
                if result is None and not cache_none:
                    return None

                # 写入缓存：写入时重新获取当前时间，并计算过期时间
                expire_at = time.time() + ttl
                self._cache[key] = (result, expire_at)
                self._cache.move_to_end(key)
                
                # 清理多余内存
                self._evict_logic()
                
                return result
            finally:
                # 锁清理：由于此 key 已处理完毕，删除锁对象释放内存
                # 下一个请求如果进来，会创建新锁，不会造成内存泄露
                if key in self._locks:
                    del self._locks[key]

    def invalidate(self, key: str):
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        self._cache.clear()
        self._locks.clear()