"""TianYuan Calendar 测试公共 fixtures。

注意：本集成测试依赖 pytest-homeassistant-custom-component（提供 pytest_homeassistant_custom_component 插件），
需在 HA 开发环境中运行（pip install -e "homeassistant[test]" 或仓库内 pytest）。
"""
from __future__ import annotations

import pytest

pytest_plugins = ("pytest_homeassistant_custom_component",)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """为所有测试自动启用自定义集成加载。"""
    yield
