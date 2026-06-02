"""
Resolve data directories for development, editable installs, and PyPI wheels.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional


def _env_data_home() -> Optional[Path]:
    raw = os.environ.get("K8S_CHAOS_HOME", "").strip()
    if raw:
        path = Path(raw).expanduser().resolve()
        if path.is_dir():
            return path
    return None


def _package_data_dir() -> Optional[Path]:
    """Bundled data inside the installed wheel (src/k8s_chaos/data)."""
    try:
        from importlib.resources import files

        root = files("k8s_chaos") / "data"
        # Traversable -> Path for Python 3.11+
        candidate = Path(str(root))
        if (candidate / "experiments" / "catalog.yaml").is_file():
            return candidate
    except Exception:
        pass
    # Fallback: filesystem next to package
    pkg = Path(__file__).resolve().parent / "data"
    if (pkg / "experiments" / "catalog.yaml").is_file():
        return pkg
    return None


def _development_repo_root() -> Optional[Path]:
    """Git checkout layout (repo root above src/k8s_chaos)."""
    here = Path(__file__).resolve().parent
    for parent in [here.parent.parent, here.parent.parent.parent]:
        if (parent / "experiments" / "catalog.yaml").is_file():
            return parent
    cwd = Path.cwd()
    if (cwd / "experiments" / "catalog.yaml").is_file():
        return cwd
    return None


@lru_cache(maxsize=1)
def data_root() -> Path:
    """
    Root directory containing experiments/, config/, workflows/, examples/.
    Priority: K8S_CHAOS_HOME > packaged data > repository checkout.
    """
    for resolver in (_env_data_home, _package_data_dir, _development_repo_root):
        root = resolver()
        if root is not None:
            return root
    raise FileNotFoundError(
        "Cannot locate k8s-chaos data files. Set K8S_CHAOS_HOME or install "
        "the package with bundled data (pip install k8s-chaos-engineering)."
    )


def repo_root() -> Path:
    """Alias used across the codebase."""
    return data_root()


def experiments_dir() -> Path:
    return data_root() / "experiments"


def config_dir() -> Path:
    return data_root() / "config"


def workflows_dir() -> Path:
    return data_root() / "workflows" / "gameday"


def examples_dir() -> Path:
    return data_root() / "examples"


def ensure_scripts_on_path() -> None:
    """Backward compatibility when running from a git clone."""
    root = data_root()
    scripts = root / "scripts"
    if scripts.is_dir():
        scripts_str = str(scripts)
        if scripts_str not in sys.path:
            sys.path.insert(0, scripts_str)
