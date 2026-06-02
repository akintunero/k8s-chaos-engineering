"""Load experiment catalog metadata."""

from __future__ import annotations

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
    return catalog.get("quickstart", {})


def list_gameday_workflows(workflows_dir_path: Optional[Path] = None) -> List[str]:
    root = workflows_dir_path or workflows_dir()
    if not root.exists():
        return []
    return sorted(p.stem for p in root.glob("*.yaml"))
