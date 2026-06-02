"""Tests for plugin registry."""

from k8s_chaos.utils.plugins import list_plugins, load_plugin_config


def test_load_plugin_config():
    data = load_plugin_config()
    assert "plugins" in data


def test_list_plugins_has_example():
    plugins = list_plugins()
    assert any(p.get("name") == "log-stress-demo" for p in plugins)
