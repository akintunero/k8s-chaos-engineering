"""
Blast-radius profiles and experiment safety checks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .config import get_config
from .logging import get_logger

logger = get_logger(__name__)

EXPERIMENT_SKIP_FILES = {
    "rbac",
    "rbac-improved",
    "catalog",
    "kustomization",
    "network-policies",
    "chaos-workflow",
    "multi-cluster-chaos",
    "custom-chaos",
}


@dataclass
class BlastRadiusProfile:
    name: str
    description: str
    allowed_experiments: List[str]
    blocked_namespaces: List[str]
    max_duration_seconds: int
    require_app_healthy: bool
    require_explicit_confirm: bool = False
    allow_abort_all: bool = True


class SafetyError(Exception):
    """Raised when a chaos operation violates safety policy."""


def get_chaos_env() -> str:
    return os.getenv("CHAOS_ENV", "dev").strip().lower()


def load_blast_radius_config(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        from k8s_chaos._paths import config_dir

        path = config_dir() / "blast-radius.yaml"
    if not path.exists():
        raise SafetyError(f"Blast-radius config not found: {path}")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_profile(env: Optional[str] = None) -> BlastRadiusProfile:
    env = (env or get_chaos_env()).lower()
    data = load_blast_radius_config()
    profiles = data.get("profiles", {})
    if env not in profiles:
        raise SafetyError(f"Unknown CHAOS_ENV '{env}'. Valid: {', '.join(sorted(profiles.keys()))}")
    raw = profiles[env]
    return BlastRadiusProfile(
        name=env,
        description=raw.get("description", ""),
        allowed_experiments=list(raw.get("allowed_experiments", [])),
        blocked_namespaces=list(raw.get("blocked_namespaces", [])),
        max_duration_seconds=int(raw.get("max_duration_seconds", 60)),
        require_app_healthy=bool(raw.get("require_app_healthy", True)),
        require_explicit_confirm=bool(raw.get("require_explicit_confirm", False)),
        allow_abort_all=bool(raw.get("allow_abort_all", True)),
    )


def assert_namespace_allowed(namespace: str, profile: Optional[BlastRadiusProfile] = None) -> None:
    profile = profile or get_profile()
    if namespace in profile.blocked_namespaces:
        raise SafetyError(f"Namespace '{namespace}' is blocked for CHAOS_ENV={profile.name}")


def assert_experiment_allowed(
    experiment_name: str,
    profile: Optional[BlastRadiusProfile] = None,
    *,
    confirmed: bool = False,
) -> None:
    profile = profile or get_profile()
    allowed = profile.allowed_experiments
    if experiment_name not in allowed:
        raise SafetyError(
            f"Experiment '{experiment_name}' is not allowed for CHAOS_ENV={profile.name}. " f"Allowed: {', '.join(allowed)}"
        )
    if profile.require_explicit_confirm and not confirmed:
        if os.getenv("CHAOS_CONFIRM", "").lower() not in ("yes", "true", "1"):
            raise SafetyError(f"CHAOS_ENV={profile.name} requires CHAOS_CONFIRM=yes to run experiments")


def is_experiment_file(name: str) -> bool:
    return name not in EXPERIMENT_SKIP_FILES
