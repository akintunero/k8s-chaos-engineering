"""Tests for SLO evaluation helpers."""

from unittest.mock import patch

import pytest

from k8s_chaos.utils.slo import (
    ProbeResult,
    aggregate_steps_verdict,
    default_probes_for_experiment,
)


def test_aggregate_steps_verdict_pass():
    steps = [{"verdict": "PASS"}, {"verdict": "PASS"}]
    assert aggregate_steps_verdict(steps) == "PASS"


def test_aggregate_steps_verdict_fail():
    steps = [{"verdict": "PASS"}, {"verdict": "FAIL"}]
    assert aggregate_steps_verdict(steps) == "FAIL"


def test_default_probes_fallback():
    probes = default_probes_for_experiment({}, expected_replicas=3, recovery_timeout=60)
    assert len(probes) >= 2
    assert probes[0]["type"] == "deployment_ready"


def test_slo_evaluation_verdict_from_probes():
    from k8s_chaos.utils.slo import SloEvaluation

    ev = SloEvaluation(experiment="pod-delete", hypothesis="test")
    ev.probes = [
        ProbeResult("a", "deployment_ready", "PASS", "ok"),
        ProbeResult("b", "pods_ready_ratio", "PASS", "ok"),
    ]
    assert ev.verdict == "PASS"


@patch("k8s_chaos.utils.slo.run_command")
def test_deployment_ready_probe_fail(mock_run):
    from k8s_chaos.utils.slo import run_probe

    mock_run.side_effect = lambda *args, **kwargs: "0" if "readyReplicas" in args[0] else "3"
    result = run_probe(
        {
            "name": "dep",
            "type": "deployment_ready",
            "min_ready_replicas": 3,
            "max_recovery_seconds": 1,
        },
        namespace="hello-world-app",
        deployment="flask-app",
        expected_replicas=3,
        recovery_timeout=1,
        interval=1,
    )
    assert result.verdict == "FAIL"
