"""TianYuan 实体基类."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TianYuanCoordinator

class TianYuanBaseEntity(CoordinatorEntity[TianYuanCoordinator]):
    """天元集成所有实体的共同基类."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TianYuanCoordinator) -> None:
        """初始化基类."""
        super().__init__(coordinator)

    @property
    def device_info(self):
        # 始终指向主设备
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """判断实体是否可用."""
        return super().available and self.coordinator.data is not None

class TianYuanQihuangBaseEntity(TianYuanBaseEntity):
    """子设备基类：天元岐黄 (中医)"""
    @property
    def device_info(self):
        return self.coordinator.qihuang_device_info

class TianYuanShushuBaseEntity(TianYuanBaseEntity):
    """子设备基类：天元术数 (易理)"""
    @property
    def device_info(self):
        return self.coordinator.shushu_device_info
    
