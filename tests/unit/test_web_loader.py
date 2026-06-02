"""Tests for web backend module loader."""

import sys
from pathlib import Path


def test_load_chaos_modules():
    repo = Path(__file__).resolve().parents[2]
    backend = str(repo / "web" / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)

    from loader import load_chaos_modules

    mods = load_chaos_modules()
    assert "chaos_runner" in mods
    assert hasattr(mods["chaos_runner"], "list_experiments")
