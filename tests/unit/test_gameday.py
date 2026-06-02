"""Tests for GameDay workflow definitions."""

from pathlib import Path

import yaml

from k8s_chaos.utils.catalog import list_gameday_workflows, load_catalog, repo_root


def test_gameday_workflows_exist():
    names = list_gameday_workflows()
    assert "quickstart" in names
    assert "resilience-basics" in names


def test_quickstart_workflow_schema():
    path = repo_root() / "workflows" / "gameday" / "quickstart.yaml"
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert data["name"] == "quickstart"
    assert len(data["steps"]) >= 2
    types = {s["type"] for s in data["steps"]}
    assert "probe" in types
    assert "experiment" in types


def test_catalog_lists_gamedays():
    catalog = load_catalog()
    gamedays = catalog.get("gamedays", [])
    names = {g["name"] for g in gamedays}
    assert "quickstart" in names
