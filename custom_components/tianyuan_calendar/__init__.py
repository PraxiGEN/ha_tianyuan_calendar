"""TianYuan 集成入口"""
from __future__ import annotations

import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_integration
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import frontend

from .const import (
    DOMAIN,
    PLATFORMS,
    LOGGER,
    CONF_ENABLE_QIHUANG,
    CONF_ENABLE_SHUSHU,
    CONF_SYS_TOKEN,
    QIHUANG_PRIVATE_KEYS,
    SHUSHU_PRIVATE_KEYS,
)
from .coordinator import TianYuanCoordinator
from .tianyuan.library import 检查专业权限类

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
            card_url = f"/{DOMAIN}-local/tianyuan-lunar-card.js?v={version}"
            frontend.add_extra_js_url(hass, card_url)
            LOGGER.info("TianYuan 卡片资源已注册: %s", card_url)

        hass.data[f"{DOMAIN}_assets"] = True

    coordinator = TianYuanCoordinator(hass, entry, version)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # 注册表准备
    device_registry = dr.async_get(hass)
    # 定义各设备的标识符 (Identifiers)
    main_device_ident = (DOMAIN, entry.entry_id)
    shushu_device_ident = (DOMAIN, f"{entry.entry_id}_shushu")
    qihuang_device_ident = (DOMAIN, f"{entry.entry_id}_qihuang") # 新增：岐黄设备ID
    # 显式注册主设备，确保子设备通过 via_device 关联时主设备已存在且名称可本地化
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={main_device_ident},
        translation_key="tianyuan_lunar",
        manufacturer="TianYuan Calendar",
        sw_version=version,
        entry_type="service",
    )

    # 可选/隐私实体采用「按需创建」策略：
    if entry.options.get(CONF_ENABLE_SHUSHU):
        # 开启时：创建/更新术数设备
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={shushu_device_ident},
            translation_key="tianyuan_shushu",
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
            translation_key="tianyuan_qihuang",
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

    # 清理失效的自用实体：所属开关关闭或系统令牌失效时，移除对应私有实体，避免僵尸残留
    conf = {**entry.data, **entry.options}
    has_pro_access = 检查专业权限类(conf.get(CONF_SYS_TOKEN, ""))
    _cleanup_private_entities(hass, entry, has_pro_access)

    # 转发平台设置并监听更新
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

def _cleanup_private_entities(hass: HomeAssistant, entry: TianYuanConfigEntry, has_pro_access: bool) -> None:
    """清除不再符合条件的自用实体，避免僵尸实体残留。"""
    reg = er.async_get(hass)
    conf = {**entry.data, **entry.options}
    qihuang_available = bool(conf.get(CONF_ENABLE_QIHUANG)) and has_pro_access
    shushu_available = bool(conf.get(CONF_ENABLE_SHUSHU)) and has_pro_access
    for entity in list(er.async_entries_for_config_entry(reg, entry.entry_id)):
        uid = entity.unique_id
        if not uid or not uid.startswith(f"{entry.entry_id}_"):
            continue
        key = uid[len(entry.entry_id) + 1:]
        try:
            if key in QIHUANG_PRIVATE_KEYS and not qihuang_available:
                reg.async_remove(entity.entity_id)
                LOGGER.info("已清除岐黄自用实体: %s", entity.entity_id)
            elif key in SHUSHU_PRIVATE_KEYS and not shushu_available:
                reg.async_remove(entity.entity_id)
                LOGGER.info("已清除术数自用实体: %s", entity.entity_id)
        except Exception as err:  # 实体已被其它路径（如子设备删除）移除时静默跳过
            LOGGER.debug("清理自用实体 %s 时忽略: %s", entity.entity_id, err)

async def async_update_options(hass: HomeAssistant, entry: TianYuanConfigEntry) -> None:
    """当用户在集成选项中点击保存时触发。"""
    LOGGER.debug("检测到配置选项更新，正在重新加载集成...")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """卸载集成实例."""
    LOGGER.debug("正在卸载 TianYuan 集成实例: %s", entry.entry_id)
    # 卸载所有平台
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
