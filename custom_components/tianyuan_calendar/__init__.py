"""
TianYuan (天元农历) - 核心集成引导文件
"""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration

from .const import DOMAIN, PLATFORMS, LOGGER, CONF_ENABLE_SHUSHU, CONF_ENABLE_MORE
from .coordinator import TianYuanCoordinator

# 定义配置条目类型
type TianYuanConfigEntry = ConfigEntry[TianYuanCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """设置 TianYuan 集成实例."""
    

    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) if integration.version else "1.0.0"

    coordinator = TianYuanCoordinator(hass, entry, version)
    
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = coordinator

    # 1. 注册/同步设备
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    
    # 定义两个设备的 ID
    main_device_ident = (DOMAIN, entry.entry_id)
    shushu_device_ident = (DOMAIN, f"{entry.entry_id}_shushu")

    # 2. 清理逻辑更多实体
    if not entry.options.get(CONF_ENABLE_MORE):
        
        more_entity_keys = ["tst_time", "bazi", "ganzhi", "twelve_gods", "chongsha", "xingxiu", "season"]
        
        # 获取该配置条目下的所有已注册实体
        existing_entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        for ent in existing_entities:
            # 通过 unique_id 的后缀来识别这些实体
            if any(ent.unique_id.endswith(key) for key in more_entity_keys):
                LOGGER.info("更多实体开关已关闭，正在移除实体: %s", ent.entity_id)
                entity_registry.async_remove(ent.entity_id)

    # 3. 处理术数设备逻辑
    if entry.options.get(CONF_ENABLE_SHUSHU):
        # 开启时：创建/更新术数设备
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={shushu_device_ident},
            name="TianYuan ShuShu",
            manufacturer="TianYuan ShuShu",
            via_device=main_device_ident,
        )
    else:
        # 关闭时：主动从注册表中移除该设备，解决“设备还在”的问题
        device = device_registry.async_get_device(identifiers={shushu_device_ident})
        if device:
            LOGGER.info("术数模式已关闭，正在清理术数设备...")
            device_registry.async_remove_device(device.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_update_options(hass: HomeAssistant, entry: TianYuanConfigEntry) -> None:
    """当用户在集成选项中点击保存时触发。"""
    LOGGER.debug("检测到配置选项更新，正在重新加载集成...")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """卸载集成实例."""
    LOGGER.debug("正在卸载 TianYuan 集成实例: %s", entry.entry_id)
    
    # 卸载所有平台
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    return unload_ok
