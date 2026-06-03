#!/usr/bin/env python3
"""
Verify local prerequisites for the chaos engineering quickstart.
"""

from __future__ import annotations

import sys

from k8s_chaos.utils import get_config, get_logger, run_command

logger = get_logger(__name__)


def check_tool(name: str, version_cmd: str | None = None) -> bool:
    if not run_command(f"which {name}", check=False):
        logger.error(f"Missing required tool: {name}")
        return False
    if version_cmd:
        version = run_command(version_cmd, check=False)
        logger.info(f"OK {name}: {(version or '').splitlines()[0]}")
    else:
        logger.info(f"OK {name}")
    return True


def check_cluster() -> bool:
    info = run_command("kubectl cluster-info", check=False)
    if not info:
        logger.error("kubectl cannot reach a cluster (kubectl cluster-info failed)")
        return False
    logger.info("OK Kubernetes cluster reachable")
    return True


def check_litmus(namespace: str) -> bool:
    pods = run_command(f"kubectl get pods -n {namespace} --no-headers", check=False)
    if not pods:
        logger.warning(f"Litmus namespace '{namespace}' has no pods (install with make install-litmus)")
        return False
    logger.info(f"OK Litmus namespace '{namespace}' has running resources")
    return True


def check_quickstart_app(namespace: str) -> bool:
    ready = run_command(
        f"kubectl get deployment flask-app -n {namespace} " "-o jsonpath='{.status.readyReplicas}'",
        check=False,
    )
    desired = run_command(
        f"kubectl get deployment flask-app -n {namespace} " "-o jsonpath='{.spec.replicas}'",
        check=False,
    )
    if not ready or not desired:
        logger.warning(f"Quickstart app not ready in '{namespace}' " "(deploy with kubectl apply -k examples/quickstart)")
        return False
    logger.info(f"OK Quickstart app replicas {ready}/{desired}")
    return True


def main() -> None:
    config = get_config()
    logger.info("Chaos Engineering Doctor")
    logger.info("=" * 30)

    ok = True
    ok = (
        check_tool(
            "kubectl",
            "kubectl version --client --short 2>/dev/null || kubectl version --client",
        )
        and ok
    )
    ok = check_tool("helm", "helm version --short") and ok
    ok = check_tool("python3", "python3 --version") and ok
    ok = check_cluster() and ok

    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        ok = check_litmus(config.litmus_namespace) and ok
        ok = check_quickstart_app(config.app_namespace) and ok

    if ok:
        logger.info("Doctor checks passed.")
        sys.exit(0)
    logger.error("Doctor checks failed.")
    sys.exit(1)


if __name__ == "__main__":
    main()
