"""
Optional experiment plugins — register custom manifest generators.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from .catalog import repo_root
from .logging import get_logger

logger = get_logger(__name__)

ManifestGenerator = Callable[[Dict[str, Any]], str]


def _plugins_config_path() -> Path:
    from k8s_chaos._paths import config_dir

    return config_dir() / "plugins.yaml"


def load_plugin_config() -> Dict[str, Any]:
    path = _plugins_config_path()
    if not path.exists():
        return {"plugins": []}
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def list_plugins() -> List[Dict[str, Any]]:
    return load_plugin_config().get("plugins", [])


def get_plugin_generator(name: str) -> Optional[ManifestGenerator]:
    for plugin in list_plugins():
        if plugin.get("name") != name or not plugin.get("enabled", True):
            continue
        module_path = plugin.get("module")
        func_name = plugin.get("function", "generate_manifest")
        if not module_path:
            return None
        mod = importlib.import_module(module_path)
        fn = getattr(mod, func_name, None)
        if callable(fn):
            return fn
    return None


def generate_plugin_manifest(plugin_name: str, params: Dict[str, Any]) -> str:
    generator = get_plugin_generator(plugin_name)
    if generator is None:
        raise ValueError(f"Plugin not found or disabled: {plugin_name}")
    return generator(params)
