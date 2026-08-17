"""Diagnostics support for TianYuan Calendar."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_SYS_TOKEN
from . import TianYuanConfigEntry

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: TianYuanConfigEntry
) -> dict[str, Any]:
    """返回配置条目诊断信息。"""
    coordinator = entry.runtime_data
    options = async_redact_data(dict(entry.options), {CONF_SYS_TOKEN})
    diagnostics: dict[str, Any] = {
        "domain": DOMAIN,
        "version": entry.version,
        "options": options,
    }
    if coordinator.data:
        diagnostics["data_keys"] = sorted(coordinator.data.keys())

    return diagnostics

async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: TianYuanConfigEntry,
    device: Any,
) -> dict[str, Any]:
    """返回设备级诊断。"""
    return await async_get_config_entry_diagnostics(hass, entry)
