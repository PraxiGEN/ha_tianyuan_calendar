"""TianYuan 实体基类."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TianYuanCoordinator

class TianYuanBaseEntity(CoordinatorEntity[TianYuanCoordinator]):
    """天元集成所有实体的共同基类."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TianYuanCoordinator) -> None:
        """初始化基类."""
        super().__init__(coordinator)

        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """判断实体是否可用."""
        
        return super().available and self.coordinator.data is not None
