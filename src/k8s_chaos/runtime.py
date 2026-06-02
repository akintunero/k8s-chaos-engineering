"""Runtime dependencies outside the Python package (kubectl, helm, cluster)."""

from __future__ import annotations

import shutil
import sys
from typing import Iterable, List

RUNTIME_TOOLS = ("kubectl", "helm")


def missing_tools(tools: Iterable[str] = RUNTIME_TOOLS) -> List[str]:
    return [name for name in tools if shutil.which(name) is None]


def require_runtime_tools(tools: Iterable[str] = RUNTIME_TOOLS) -> None:
    """Exit with a clear message if kubectl/helm are not on PATH."""
    missing = missing_tools(tools)
    if not missing:
        return
    joined = ", ".join(missing)
    print(
        f"Missing required tools: {joined}\n"
        "Install them and ensure they are on PATH, then run:\n"
        "  k8s-chaos doctor\n"
        "Chaos commands need kubectl, helm, and a reachable Kubernetes cluster.\n"
        "See docs/version-matrix.md and docs/pypi.md.",
        file=sys.stderr,
    )
    sys.exit(1)


def command_needs_runtime_tools(command: str, args) -> bool:
    """Return True when the subcommand talks to a cluster."""
    if command == "doctor":
        return False
    if command == "list":
        return False
    if command == "gameday" and getattr(args, "list", False):
        return False
    if (
        command == "clusters"
        and not getattr(args, "experiment", None)
        and not getattr(args, "gameday", None)
    ):
        return False
    return True
