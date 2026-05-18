"""Config flow for TianYuan (天元农历)."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_REFRESH_INTERVAL,
    CONF_CUSTOM_LONGITUDE,
    CONF_ENABLE_SHUSHU,
    CONF_ENABLE_MORE,
    CONF_CALC_MODE,
    MODE_ST,
    MODE_TST,
    DEFAULT_REFRESH_INTERVAL,
)

class TianYuanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理初次安装和重新配置流程."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """初次安装：仅显示经度和频率."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # 初始化默认隐藏的选项
            options = {
                CONF_CUSTOM_LONGITUDE: float(user_input[CONF_CUSTOM_LONGITUDE]),
                CONF_REFRESH_INTERVAL: int(user_input[CONF_REFRESH_INTERVAL]),
                CONF_ENABLE_SHUSHU: False,   # 默认关闭
                CONF_ENABLE_MORE: False,  # 默认关闭
                CONF_CALC_MODE: MODE_ST,  # 默认兼容模式
            }
            return self.async_create_entry(title="天元农历", data={}, options=options)

        lon = float(self.hass.config.longitude or 120.0)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CUSTOM_LONGITUDE, default=lon): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=-180, max=180, step="any", mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_REFRESH_INTERVAL, default=DEFAULT_REFRESH_INTERVAL): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=1440, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TianYuanOptionsFlowHandler()

class TianYuanOptionsFlowHandler(config_entries.OptionsFlow):
    """配置修改界面：显示所有高级选项."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self.config_entry.options
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                # 1. 基础配置
                vol.Required(CONF_CUSTOM_LONGITUDE, default=float(opts.get(CONF_CUSTOM_LONGITUDE, 120.0))): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=-180, max=180, step="any", mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_REFRESH_INTERVAL, default=int(opts.get(CONF_REFRESH_INTERVAL, 1))): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=1440, step=1, mode=selector.NumberSelectorMode.BOX)
                ),
                # 2. 模式选择 (下拉菜单)
                vol.Required(CONF_CALC_MODE, default=opts.get(CONF_CALC_MODE, MODE_ST)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[MODE_ST, MODE_TST],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key=CONF_CALC_MODE
                    )
                ),
                # 3. 功能开关
                vol.Required(CONF_ENABLE_MORE, default=bool(opts.get(CONF_ENABLE_MORE, False))): selector.BooleanSelector(),
                vol.Required(CONF_ENABLE_SHUSHU, default=bool(opts.get(CONF_ENABLE_SHUSHU, False))): selector.BooleanSelector(),
            })
        )
