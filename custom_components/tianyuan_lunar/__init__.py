"""
TianYuan (天元农历) - 2026 Standard Integration Entry
"""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant, 
    ServiceCall, 
    ServiceResponse, 
    SupportsResponse
)
from homeassistant.helpers import device_registry as dr
from homeassistant.loader import async_get_integration

from .const import DOMAIN, PLATFORMS, LOGGER
from .coordinator import TianYuanCoordinator

type TianYuanConfigEntry = ConfigEntry[TianYuanCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """设置 TianYuan 集成实例."""
    
    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) if integration.version else "1.1.0"

    coordinator = TianYuanCoordinator(hass, entry, version)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # 注册设备
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name="TianYuan Lunar",
        manufacturer="TianYuan Lunar",
        sw_version=version,
        entry_type="service",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_update_options(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """卸载集成实例."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
