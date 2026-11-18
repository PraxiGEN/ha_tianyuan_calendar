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
    CONF_ENABLE_MORE,
    CONF_ENABLE_QIHUANG,
    CONF_ENABLE_SHUSHU,
    CONF_ENABLE_CARD,
    CONF_PRO_FEATURES,
    MORE_KEYS,
    QIHUANG_CORE_KEYS,
    SHUSHU_CORE_KEYS,
    QIHUANG_PRO_KEYS,
    SHUSHU_PRO_KEYS,
)
from .coordinator import TianYuanCoordinator

# 定义配置条目类型
type TianYuanConfigEntry = ConfigEntry[TianYuanCoordinator]

def _find_device(registry: dr.DeviceRegistry, entry_id: str, ident: tuple[str, str]) -> dr.DeviceEntry | None:
    """按标识符在配置项设备中查找，替代弃用的 async_get_device。"""
    return next((d for d in dr.async_entries_for_config_entry(registry, entry_id) if ident in d.identifiers), None)

async def async_setup_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """设置 TianYuan 集成实例."""

    integration = await async_get_integration(hass, DOMAIN)
    version = str(integration.version) if integration.version else "1.0.0"

    # 前端卡片资源：仅当「前端卡片」开关开启时才注册静态路径并注入 JS，避免全局注册
    if entry.options.get(CONF_ENABLE_CARD):
        # 静态资源路径只注册一次（重复注册会抛错），用独立标志防重复
        if f"{DOMAIN}_assets" not in hass.data:
            local_path = hass.config.path("custom_components", DOMAIN, "www")
            path_exists = await hass.async_add_executor_job(os.path.exists, local_path)
            if path_exists:
                await hass.http.async_register_static_paths([
                    StaticPathConfig(f"/{DOMAIN}-local", local_path, False)
                ])
                # 注册资源 URL 携带集成版本号：升版后 URL 随之变化，自然绕开浏览器旧缓存
                card_url = f"/{DOMAIN}-local/tianyuan-lunar-card.js?v={version}"
                frontend.add_extra_js_url(hass, card_url)
                LOGGER.info("TianYuan 卡片资源已注册: %s", card_url)
            hass.data[f"{DOMAIN}_assets"] = True
    else:
        # 开关未启用：不向全局前端注入资源（避免无条件污染所有前端）
        LOGGER.debug("前端卡片开关未启用，跳过 Lovelace 资源注册")

    coordinator = TianYuanCoordinator(hass, entry, version)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # 注册表准备
    device_registry = dr.async_get(hass)
    # 定义各设备的标识符 (Identifiers)
    main_device_ident = (DOMAIN, entry.entry_id)
    shushu_device_ident = (DOMAIN, f"{entry.entry_id}_shushu")
    qihuang_device_ident = (DOMAIN, f"{entry.entry_id}_qihuang") # 新增：岐黄设备ID
    # 三设备平级独立注册：服务集成无硬件拓扑，via_device 属弃用 API（2027.8 移除），不接父子链
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={main_device_ident},
        translation_key="tianyuan_lunar",
        manufacturer="TianYuan Calendar",
        sw_version=version,
        entry_type="service",
    )

    # 可选/隐私实体采用「按需创建」策略：
    shushu_device = qihuang_device = None
    if entry.options.get(CONF_ENABLE_SHUSHU):
        # 开启时：创建/更新术数设备
        shushu_device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={shushu_device_ident},
            translation_key="tianyuan_shushu",
            manufacturer="TianYuan Calendar",
            sw_version=version,
        )
    else:
        device = _find_device(device_registry, entry.entry_id, shushu_device_ident)
        if device:
            LOGGER.info("术数模式已关闭，正在清理术数设备...")
            device_registry.async_remove_device(device.id)

    if entry.options.get(CONF_ENABLE_QIHUANG):
        # 开启时：创建/更新岐黄设备
        qihuang_device = device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={qihuang_device_ident},
            translation_key="tianyuan_qihuang",
            manufacturer="TianYuan Calendar",
            sw_version=version,
        )
    else:
        # 关闭时：清理岐黄设备
        device = _find_device(device_registry, entry.entry_id, qihuang_device_ident)
        if device:
            LOGGER.info("岐黄模式已关闭，正在清理岐黄设备...")
            device_registry.async_remove_device(device.id)

    # 清空存量安装残留的 via_device_id：注册时省略该参数不会清除旧值，须显式置空
    for device in (shushu_device, qihuang_device):
        if device and device.via_device_id:
            device_registry.async_update_device(device.id, via_device_id=None)

    # 清理失效的门控实体：对应开关关闭后移除注册表残留，避免僵尸实体
    _cleanup_gated_entities(hass, entry)

    # 转发平台设置并监听更新
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

def _cleanup_gated_entities(hass: HomeAssistant, entry: TianYuanConfigEntry) -> None:
    """按开关门控清除不再生成的实体注册表记录。"""
    reg = er.async_get(hass)
    conf = {**entry.data, **entry.options}
    pro = bool(conf.get(CONF_PRO_FEATURES))
    gated = {
        MORE_KEYS: bool(conf.get(CONF_ENABLE_MORE)),
        QIHUANG_CORE_KEYS: bool(conf.get(CONF_ENABLE_QIHUANG)),
        SHUSHU_CORE_KEYS: bool(conf.get(CONF_ENABLE_SHUSHU)),
        QIHUANG_PRO_KEYS: bool(conf.get(CONF_ENABLE_QIHUANG)) and pro,
        SHUSHU_PRO_KEYS: bool(conf.get(CONF_ENABLE_SHUSHU)) and pro,
    }
    for entity in list(er.async_entries_for_config_entry(reg, entry.entry_id)):
        uid = entity.unique_id
        if not uid or not uid.startswith(f"{entry.entry_id}_"):
            continue
        key = uid[len(entry.entry_id) + 1:]
        if not any(key in keys and not enabled for keys, enabled in gated.items()):
            continue
        try:
            reg.async_remove(entity.entity_id)
            LOGGER.info("已清除关闭开关后的残留实体: %s", entity.entity_id)
        except Exception as err:  # 实体已被其它路径（如子设备删除）移除时静默跳过
            LOGGER.debug("清理实体 %s 时忽略: %s", entity.entity_id, err)

async def async_update_options(hass: HomeAssistant, entry: TianYuanConfigEntry) -> None:
    """当用户在集成选项中点击保存时触发。"""
    LOGGER.debug("检测到配置选项更新，正在重新加载集成...")
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: TianYuanConfigEntry) -> bool:
    """卸载集成实例."""
    LOGGER.debug("正在卸载 TianYuan 集成实例: %s", entry.entry_id)
    # 卸载所有平台
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)