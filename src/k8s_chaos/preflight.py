#!/usr/bin/env python3
"""
Pre-flight checks before running chaos experiments.
"""

from __future__ import annotations

import argparse
import sys

from k8s_chaos.utils import get_config, get_logger, run_command
from k8s_chaos.utils.k8s import wait_for_deployment
from k8s_chaos.utils.safety import assert_namespace_allowed, get_profile

logger = get_logger(__name__)


def check_cluster() -> bool:
    ok = bool(run_command("kubectl cluster-info", check=False))
    if ok:
        logger.info("OK cluster reachable")
    else:
        logger.error("Cluster not reachable")
    return ok


def check_litmus(namespace: str) -> bool:
    pods = run_command(f"kubectl get pods -n {namespace} --no-headers", check=False)
    if not pods:
        logger.error(f"No pods in Litmus namespace '{namespace}'")
        return False
    not_ready = [line for line in pods.splitlines() if line and "Running" not in line and "Completed" not in line]
    if not_ready:
        logger.warning(f"Some Litmus pods not Running: {len(not_ready)}")
    logger.info(f"OK Litmus namespace '{namespace}'")
    return True


def check_app_healthy(namespace: str, deployment: str) -> bool:
    try:
        wait_for_deployment(
            namespace=namespace,
            deployment=deployment,
            timeout=60,
            check_interval=5,
        )
        logger.info(f"OK deployment/{deployment} available in {namespace}")
        return True
    except Exception as exc:
        logger.error(f"App not healthy: {exc}")
        return False


def check_no_running_chaos(namespace: str) -> bool:
    engines = run_command(
        f"kubectl get chaosengine -n {namespace} --no-headers",
        check=False,
    )
    if engines:
        logger.error(f"ChaosEngine resources already exist in {namespace}. " "Run: python3 scripts/chaos-runner.py abort")
        return False
    logger.info(f"OK no ChaosEngine resources in {namespace}")
    return True


def run_preflight(
    namespace: str | None = None,
    *,
    require_litmus: bool = True,
    require_app: bool = True,
    require_no_chaos: bool = True,
) -> bool:
    config = get_config()
    profile = get_profile()
    namespace = namespace or config.app_namespace
    deployment = "flask-app"

    assert_namespace_allowed(namespace, profile)

    ok = check_cluster()
    if require_litmus:
        ok = check_litmus(config.litmus_namespace) and ok
    if require_app and profile.require_app_healthy:
        ok = check_app_healthy(namespace, deployment) and ok
    if require_no_chaos:
        ok = check_no_running_chaos(namespace) and ok

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Chaos experiment pre-flight checks")
    parser.add_argument("--namespace", default=None)
    parser.add_argument("--skip-litmus", action="store_true")
    parser.add_argument("--skip-app", action="store_true")
    args = parser.parse_args()

    logger.info(f"Pre-flight (CHAOS_ENV={get_profile().name})")
    if not run_preflight(
        args.namespace,
        require_litmus=not args.skip_litmus,
        require_app=not args.skip_app,
    ):
        sys.exit(1)
    logger.info("Pre-flight passed")


if __name__ == "__main__":
    main()
