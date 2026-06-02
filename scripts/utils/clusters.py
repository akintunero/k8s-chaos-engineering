"""
Multi-cluster registry and context switching.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .logging import get_logger
from .safety import SafetyError, get_chaos_env

logger = get_logger(__name__)


@dataclass
class ClusterProfile:
    name: str
    context: str
    chaos_env: str
    default_namespace: str = "hello-world-app"
    allowed_experiments: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class ClusterPolicies:
    allow_prod: bool = False
    require_confirm_for: List[str] = field(default_factory=lambda: ["prod"])


def _config_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    path = Path(os.getenv("CLUSTERS_CONFIG", root / "config" / "clusters.yaml"))
    if not path.exists():
        example = root / "config" / "clusters.yaml.example"
        if example.exists():
            logger.warning("clusters.yaml not found; using clusters.yaml.example")
            return example
    return path


def load_clusters_config(path: Optional[Path] = None) -> Dict[str, Any]:
    cfg_path = path or _config_path()
    if not cfg_path.exists():
        return {"clusters": [], "policies": {}}
    with open(cfg_path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_policies(data: Optional[Dict[str, Any]] = None) -> ClusterPolicies:
    data = data or load_clusters_config()
    raw = data.get("policies", {})
    return ClusterPolicies(
        allow_prod=bool(raw.get("allow_prod", False)),
        require_confirm_for=list(raw.get("require_confirm_for", ["prod"])),
    )


def list_clusters(path: Optional[Path] = None) -> List[ClusterProfile]:
    data = load_clusters_config(path)
    clusters: List[ClusterProfile] = []
    for raw in data.get("clusters", []):
        if not raw.get("enabled", True):
            continue
        clusters.append(
            ClusterProfile(
                name=raw["name"],
                context=raw["context"],
                chaos_env=raw.get("chaos_env", "dev"),
                default_namespace=raw.get("default_namespace", "hello-world-app"),
                allowed_experiments=list(raw.get("allowed_experiments", [])),
                enabled=True,
            )
        )
    return clusters


def get_cluster(name: str) -> ClusterProfile:
    for cluster in list_clusters():
        if cluster.name == name:
            return cluster
    raise SafetyError(f"Unknown cluster '{name}'. See config/clusters.yaml")


def resolve_clusters(
    names: Optional[List[str]],
    *,
    allow_prod: bool = False,
) -> List[str]:
    all_clusters = list_clusters()
    if not names:
        return [c.name for c in all_clusters]

    policies = load_policies()
    resolved = []
    for name in names:
        cluster = get_cluster(name)
        if cluster.chaos_env in policies.require_confirm_for and not allow_prod:
            if not policies.allow_prod:
                raise SafetyError(
                    f"Cluster '{name}' uses CHAOS_ENV={cluster.chaos_env}. "
                    "Set allow_prod in policies and pass --allow-prod to proceed."
                )
            if os.getenv("CHAOS_CONFIRM", "").lower() not in ("yes", "true", "1"):
                raise SafetyError(
                    f"Cluster '{name}' requires CHAOS_CONFIRM=yes for env={cluster.chaos_env}"
                )
        resolved.append(name)
    return resolved


def assert_experiment_allowed_on_cluster(
    cluster: ClusterProfile, experiment: str
) -> None:
    if not cluster.allowed_experiments:
        return
    if experiment not in cluster.allowed_experiments:
        raise SafetyError(
            f"Experiment '{experiment}' not allowed on cluster '{cluster.name}'"
        )


def current_context() -> Optional[str]:
    from .k8s import run_command

    return run_command("kubectl config current-context", check=False)


def use_context(context: str) -> None:
    from .k8s import run_command

    result = run_command(f"kubectl config use-context {context}", check=False)
    if result is None:
        raise SafetyError(f"Failed to switch to context '{context}'")


class cluster_context:
    """Switch kubectl context for the duration of a block."""

    def __init__(self, context: str):
        self.context = context
        self._previous: Optional[str] = None

    def __enter__(self):
        self._previous = current_context()
        use_context(self.context)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._previous:
            use_context(self._previous)
        return False


def apply_cluster_env(cluster: ClusterProfile) -> Dict[str, str]:
    """Return env overrides for a cluster run."""
    return {
        "CHAOS_ENV": cluster.chaos_env,
        "APP_NAMESPACE": cluster.default_namespace,
    }
