"""Load experiment catalog metadata."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from k8s_chaos._paths import data_root, experiments_dir, workflows_dir

from .logging import get_logger

logger = get_logger(__name__)


def repo_root() -> Path:
    return data_root()


def load_catalog(path: Optional[Path] = None) -> Dict[str, Any]:
    catalog_path = path or (experiments_dir() / "catalog.yaml")
    with open(catalog_path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_experiment_meta(catalog: Dict[str, Any], experiment_name: str) -> Dict[str, Any]:
    for item in catalog.get("experiments", []):
        if item.get("name") == experiment_name:
            return item
    return {}


def get_quickstart_settings(catalog: Dict[str, Any]) -> Dict[str, Any]:
    settings = dict(catalog.get("quickstart", {}))
    if os.getenv("K8S_CHAOS_E2E", "").lower() in ("1", "true", "yes"):
        min_ready = int(os.getenv("K8S_CHAOS_E2E_MIN_READY", "1"))
        settings["expected_replicas"] = min(int(settings.get("expected_replicas", 3)), min_ready)
        settings["recovery_timeout_seconds"] = int(
            os.getenv(
                "K8S_CHAOS_RECOVERY_TIMEOUT",
                settings.get("recovery_timeout_seconds", 120),
            )
        )
    return settings


def adjust_probes_for_e2e(probes: List[Dict[str, Any]], expected_replicas: int) -> List[Dict[str, Any]]:
    if os.getenv("K8S_CHAOS_E2E", "").lower() not in ("1", "true", "yes"):
        return probes
    min_ready = int(os.getenv("K8S_CHAOS_E2E_MIN_READY", "1"))
    adjusted: List[Dict[str, Any]] = []
    for probe in probes:
        entry = dict(probe)
        if entry.get("type") == "deployment_ready":
            entry["min_ready_replicas"] = min(int(entry.get("min_ready_replicas", expected_replicas)), min_ready)
        adjusted.append(entry)
    return adjusted


def list_gameday_workflows(workflows_dir_path: Optional[Path] = None) -> List[str]:
    root = workflows_dir_path or workflows_dir()
    if not root.exists():
        return []
    return sorted(p.stem for p in root.glob("*.yaml"))
