"""TianYuan Calendar 配置流测试。"""
from __future__ import annotations

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.tianyuan_calendar.const import (
    DOMAIN,
    CONF_CUSTOM_LONGITUDE,
    CONF_REFRESH_INTERVAL,
    CONF_ENABLE_MORE,
    CONF_ENABLE_QIHUANG,
    CONF_ENABLE_SHUSHU,
    CONF_ENABLE_SHENGRI,
    CONF_CALC_MODE,
)


async def test_user_flow_minimal(hass: HomeAssistant) -> None:
    """初次安装：仅填经度与刷新频率即可完成。"""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CUSTOM_LONGITUDE: 120.0,
            CONF_REFRESH_INTERVAL: 1,
        },
    )
    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == "TianYuan 天元"
    assert result2["data"] == {}
    opts = result2["options"]
    assert opts[CONF_ENABLE_MORE] is False
    assert opts[CONF_ENABLE_QIHUANG] is False
    assert opts[CONF_ENABLE_SHUSHU] is False


async def test_options_flow_birthdays_step_routing(hass: HomeAssistant) -> None:
    """选项流：开启生日开关应路由进入生日管理子页面（开关仅作为进入门控）。"""
    # 先建立条目
    entry_result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    created = await hass.config_entries.flow.async_configure(
        entry_result["flow_id"],
        {CONF_CUSTOM_LONGITUDE: 120.0, CONF_REFRESH_INTERVAL: 1},
    )
    entry_id = created["result"].entry_id

    # 选项流：开启生日开关 -> 应进入 birthdays 子步骤
    opts_result = await hass.config_entries.options.async_init(entry_id)
    assert opts_result["type"] == data_entry_flow.FlowResultType.FORM
    assert opts_result["step_id"] == "init"

    routed = await hass.config_entries.options.async_configure(
        opts_result["flow_id"],
        {
            CONF_CUSTOM_LONGITUDE: 120.0,
            CONF_REFRESH_INTERVAL: 1,
            CONF_CALC_MODE: MODE_ST,
            CONF_ENABLE_MORE: False,
            CONF_ENABLE_QIHUANG: False,
            CONF_ENABLE_SHUSHU: False,
            CONF_ENABLE_SHENGRI: True,
        },
    )
    assert routed["type"] == data_entry_flow.FlowResultType.FORM
    assert routed["step_id"] == "birthdays"
