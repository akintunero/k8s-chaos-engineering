#!/usr/bin/env python3
"""
GameDay orchestrator — ordered chaos steps with SLO pass/fail gates.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import time
from typing import Any, Dict, List, Optional

import yaml

from k8s_chaos.utils import get_config, get_logger
from k8s_chaos.utils.catalog import (
    get_experiment_meta,
    get_quickstart_settings,
    list_gameday_workflows,
    load_catalog,
    repo_root,
)
from k8s_chaos.utils.reporting import print_gameday_summary, write_report
from k8s_chaos.utils.safety import assert_experiment_allowed, get_chaos_env
from k8s_chaos.utils.slo import build_report_payload, evaluate_experiment_slo, run_probe

logger = get_logger(__name__)


def _load_chaos_runner():
    from k8s_chaos import chaos_runner

    return chaos_runner


def load_workflow(name: str) -> Dict[str, Any]:
    from k8s_chaos._paths import workflows_dir

    path = workflows_dir() / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"GameDay workflow not found: {path}")
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _should_skip_step(step: Dict[str, Any]) -> Optional[str]:
    skip_envs = step.get("skip_if_chaos_env") or []
    env = get_chaos_env()
    if env in skip_envs:
        return f"skipped for CHAOS_ENV={env}"
    return None


def run_probe_step(
    step: Dict[str, Any],
    *,
    namespace: str,
    deployment: str,
    expected_replicas: int,
    recovery_timeout: int,
) -> Dict[str, Any]:
    config = get_config()
    probes_cfg = step.get("probes") or [
        {
            "name": "deployment_ready",
            "type": "deployment_ready",
            "min_ready_replicas": expected_replicas,
            "max_recovery_seconds": recovery_timeout,
        }
    ]
    results = []
    for probe_cfg in probes_cfg:
        results.append(
            run_probe(
                probe_cfg,
                namespace=namespace,
                deployment=deployment,
                expected_replicas=expected_replicas,
                recovery_timeout=recovery_timeout,
                interval=config.check_interval,
            ).to_dict()
        )
    verdict = "FAIL" if any(p["verdict"] == "FAIL" for p in results) else "PASS"
    return {
        "id": step.get("id"),
        "type": "probe",
        "description": step.get("description", ""),
        "verdict": verdict,
        "probes": results,
    }


def run_experiment_step(
    step: Dict[str, Any],
    *,
    namespace: str,
    deployment: str,
    expected_replicas: int,
    default_recovery_timeout: int,
    catalog: Dict[str, Any],
) -> Dict[str, Any]:
    chaos = _load_chaos_runner()
    run_experiment = chaos.run_experiment
    stop_experiment = chaos.stop_experiment

    experiment = step["experiment"]
    assert_experiment_allowed(experiment)

    chaos_wait = int(step.get("chaos_wait_seconds", 45))
    recovery_timeout = int(step.get("recovery_timeout_seconds", default_recovery_timeout))

    logger.info("GameDay step: running experiment %s", experiment)
    os.environ["SKIP_PREFLIGHT"] = "1"
    run_experiment(experiment, namespace)

    logger.info("Waiting %ss for chaos", chaos_wait)
    time.sleep(chaos_wait)

    meta = get_experiment_meta(catalog, experiment)
    evaluation = evaluate_experiment_slo(
        experiment,
        namespace=namespace,
        deployment=deployment,
        expected_replicas=expected_replicas,
        recovery_timeout=recovery_timeout,
        experiment_meta=meta,
    )

    if step.get("cleanup", True):
        stop_experiment(experiment, namespace)

    step_result = {
        "id": step.get("id"),
        "type": "experiment",
        "description": step.get("description", ""),
        "experiment": experiment,
        "verdict": evaluation.verdict,
        **evaluation.to_dict(),
    }
    return step_result


def run_wait_step(step: Dict[str, Any]) -> Dict[str, Any]:
    seconds = int(step.get("seconds", 10))
    logger.info("Waiting %ss (cooldown)", seconds)
    time.sleep(seconds)
    return {
        "id": step.get("id"),
        "type": "wait",
        "description": step.get("description", ""),
        "verdict": "PASS",
        "seconds": seconds,
    }


def execute_gameday(workflow_name: str, *, skip_preflight: bool = False) -> Dict[str, Any]:
    workflow = load_workflow(workflow_name)
    catalog = load_catalog()
    quickstart = get_quickstart_settings(catalog)
    config = get_config()

    namespace = workflow.get("namespace", quickstart.get("namespace", config.app_namespace))
    deployment = workflow.get("deployment", quickstart.get("deployment", "flask-app"))
    expected = int(workflow.get("expected_replicas", quickstart.get("expected_replicas", 3)))
    default_recovery = int(
        workflow.get(
            "default_recovery_timeout_seconds",
            quickstart.get("recovery_timeout_seconds", 120),
        )
    )

    if not skip_preflight:
        from k8s_chaos.preflight import run_preflight

        if not run_preflight(namespace):
            raise RuntimeError("Pre-flight checks failed")

    step_results: List[Dict[str, Any]] = []
    for step in workflow.get("steps", []):
        skip_reason = _should_skip_step(step)
        if skip_reason:
            step_results.append(
                {
                    "id": step.get("id"),
                    "type": step.get("type"),
                    "verdict": "SKIP",
                    "description": step.get("description", ""),
                    "message": skip_reason,
                }
            )
            logger.info("Skipping step %s: %s", step.get("id"), skip_reason)
            continue

        stype = step.get("type")
        if stype == "probe":
            result = run_probe_step(
                step,
                namespace=namespace,
                deployment=deployment,
                expected_replicas=expected,
                recovery_timeout=default_recovery,
            )
        elif stype == "experiment":
            result = run_experiment_step(
                step,
                namespace=namespace,
                deployment=deployment,
                expected_replicas=expected,
                default_recovery_timeout=default_recovery,
                catalog=catalog,
            )
        elif stype == "wait":
            result = run_wait_step(step)
        else:
            result = {
                "id": step.get("id"),
                "type": stype,
                "verdict": "FAIL",
                "description": f"Unknown step type: {stype}",
            }
        step_results.append(result)
        logger.info("Step %s: %s", result.get("id"), result.get("verdict"))

    from datetime import datetime, timezone

    from k8s_chaos.utils.slo import aggregate_steps_verdict

    report: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_type": "gameday",
        "gameday": workflow.get("name", workflow_name),
        "description": workflow.get("description", ""),
        "verdict": aggregate_steps_verdict(step_results),
        "namespace": namespace,
        "deployment": deployment,
        "chaos_env": get_chaos_env(),
        "steps": step_results,
    }

    if os.getenv("NOTIFICATIONS_ENABLED", "").lower() in ("1", "true", "yes"):
        try:
            from k8s_chaos.notifications import NotificationService

            NotificationService().send_notification(
                title=f"GameDay {report['gameday']}: {report['verdict']}",
                message=f"Completed with verdict {report['verdict']}",
                level="success" if report["verdict"] == "PASS" else "error",
            )
        except Exception as exc:
            logger.warning("Notification failed: %s", exc)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a GameDay chaos workflow")
    parser.add_argument(
        "workflow",
        nargs="?",
        help="GameDay workflow name (file in workflows/gameday/)",
    )
    parser.add_argument("--list", action="store_true", help="List available GameDays")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--skip-preflight", action="store_true")
    args = parser.parse_args()

    if args.list:
        names = list_gameday_workflows()
        logger.info("Available GameDays:")
        for name in names:
            logger.info("  - %s", name)
        return

    if not args.workflow:
        parser.error("workflow name required (or use --list)")

    logger.info("Starting GameDay: %s (CHAOS_ENV=%s)", args.workflow, get_chaos_env())
    report = execute_gameday(args.workflow, skip_preflight=args.skip_preflight)
    path = write_report(report, repo_root() / args.output_dir, basename=f"gameday-{args.workflow}")
    print_gameday_summary(report, path)

    if report.get("verdict") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
