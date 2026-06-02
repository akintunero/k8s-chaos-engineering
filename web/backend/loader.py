"""Load chaos automation modules from the installed k8s_chaos package."""

from __future__ import annotations

import importlib
from types import ModuleType


def load_chaos_modules() -> dict[str, ModuleType]:
    return {
        "chaos_runner": importlib.import_module("k8s_chaos.chaos_runner"),
        "scheduler": importlib.import_module("k8s_chaos.scheduler"),
        "notifications": importlib.import_module("k8s_chaos.notifications"),
    }
