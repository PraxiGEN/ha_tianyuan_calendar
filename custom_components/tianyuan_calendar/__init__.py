"""
TianYuan (天元农历) - 核心集成引导文件
"""
from __future__ import annotations

import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend

from .const import DOMAIN, PLATFORMS, LOGGER, CONF_ENABLE_QIHUANG, CONF_ENABLE_SHUSHU, CONF_ENABLE_MORE, CONF_SYS_TOKEN
from .coordinator import TianYuanCoordinator
from .tianyuan.maps_loader import 检查专业权限类

# 定义配置条目类型
type TianYuanConfigEntry = ConfigEntry[TianYuanCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """设置 TianYuan 集成实例."""

    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) if integration.version else "1.0.0"

    # 注册前端资源（仅执行一次）
    if f"{DOMAIN}_assets" not in hass.data:
        local_path = hass.config.path("custom_components", DOMAIN, "www")

        if os.path.exists(local_path):
            # 暴露静态资源路径
            await hass.http.async_register_static_paths([
                StaticPathConfig(f"/{DOMAIN}-local", local_path, False)
            ])

            # 自动注入 Lovelace 资源
            card_url = f"/{DOMAIN}-local/tianyuan-lunar-card.js?v={version}"
            frontend.add_extra_js_url(hass, card_url)

            LOGGER.info("TianYuan 卡片资源已注册: %s", card_url)

        hass.data[f"{DOMAIN}_assets"] = True

    coordinator = TianYuanCoordinator(hass, entry, version)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # 注册表准备
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    
    # 定义各设备的标识符 (Identifiers)
    main_device_ident = (DOMAIN, entry.entry_id)
    shushu_device_ident = (DOMAIN, f"{entry.entry_id}_shushu")
    qihuang_device_ident = (DOMAIN, f"{entry.entry_id}_qihuang") # 新增：岐黄设备ID

    # 清理逻辑：更多农历实体
    # 如果关闭了“更多实体”开关，主动移除那些散落在主设备下的实体
    if not entry.options.get(CONF_ENABLE_MORE):
        # 注意：这里的 key 需与你 sensor.py 中 MORE_SENSORS 定义的 key 完全一致
        more_entity_keys = ["tst_time", "sizhu_bazi", "tiangan_dizhi", "shier_tianshen", "chong_sha", "dongfang_xingxiu"]
        
        existing_entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        for ent in existing_entities:
            if any(ent.unique_id.endswith(key) for key in more_entity_keys):
                LOGGER.info("更多实体开关已关闭，正在移除实体: %s", ent.entity_id)
                entity_registry.async_remove(ent.entity_id)

    has_pro_access = 检查专业权限类(entry.options.get(CONF_SYS_TOKEN, ""))
    if not has_pro_access:

        private_keys = ["fuxingjue_zangfu_yongyaofa", "shanghan_zabinglun", "liuyao_shifa", "liuyaozhanbu_input", "fuxingjue_viscera", 
                        "symptom_selector", "shanghan_channel", "shanghan_syndrome_selector", "shanghan_formula_selector"] 
        
        existing_entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
        for ent in existing_entities:
            if any(ent.unique_id.endswith(f"_{key}") for key in private_keys):
                LOGGER.info("自用模式未开启，正在移除隐私实体: %s", ent.entity_id)
                entity_registry.async_remove(ent.entity_id)   

    if entry.options.get(CONF_ENABLE_SHUSHU):
        # 开启时：创建/更新术数设备
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={shushu_device_ident},
            name="TianYuan ShuShu",
            manufacturer="TianYuan Calendar",
            sw_version=version,
            via_device=main_device_ident,
        )
    else:
        device = device_registry.async_get_device(identifiers={shushu_device_ident})
        if device:
            LOGGER.info("术数模式已关闭，正在清理术数设备...")
            device_registry.async_remove_device(device.id)

    if entry.options.get(CONF_ENABLE_QIHUANG): 
        # 开启时：创建/更新岐黄设备
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={qihuang_device_ident},
            name="TianYuan QiHuang",
            manufacturer="TianYuan Calendar",
            sw_version=version,
            via_device=main_device_ident,
        )
    else:
        # 关闭时：清理岐黄设备
        device = device_registry.async_get_device(identifiers={qihuang_device_ident})
        if device:
            LOGGER.info("岐黄模式已关闭，正在清理岐黄设备...")
            device_registry.async_remove_device(device.id)

    # 转发平台设置 (sensor, select, text, date, button, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # 监听选项更新
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
