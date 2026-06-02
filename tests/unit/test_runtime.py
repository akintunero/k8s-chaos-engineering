"""Tests for runtime tool checks."""

import argparse

from k8s_chaos.runtime import command_needs_runtime_tools, missing_tools


def test_command_needs_runtime_tools():
    assert not command_needs_runtime_tools("doctor", argparse.Namespace())
    assert not command_needs_runtime_tools("list", argparse.Namespace())
    assert not command_needs_runtime_tools(
        "gameday", argparse.Namespace(list=True)
    )
    assert not command_needs_runtime_tools(
        "clusters", argparse.Namespace(experiment=None, gameday=None)
    )
    assert command_needs_runtime_tools("run", argparse.Namespace())
    assert command_needs_runtime_tools(
        "clusters", argparse.Namespace(experiment="pod-delete", gameday=None)
    )


def test_missing_tools_includes_unknown():
    assert "definitely-not-a-real-binary-xyz" in missing_tools(
        ("definitely-not-a-real-binary-xyz",)
    )
