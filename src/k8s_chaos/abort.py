#!/usr/bin/env python3
"""
Emergency stop: halt and remove ChaosEngine resources.
"""

from __future__ import annotations

import argparse
import sys

from k8s_chaos.utils import get_config, get_logger, run_command, validate_namespace
from k8s_chaos.utils.safety import assert_namespace_allowed, get_profile

logger = get_logger(__name__)


def abort_namespace(namespace: str) -> int:
    validate_namespace(namespace)
    assert_namespace_allowed(namespace)

    names = run_command(
        f"kubectl get chaosengine -n {namespace} -o jsonpath='{{.items[*].metadata.name}}'",
        check=False,
    )
    if not names:
        logger.info(f"No ChaosEngine resources in {namespace}")
        return 0

    count = 0
    for name in names.split():
        run_command(
            f"kubectl patch chaosengine {name} -n {namespace} "
            "--type='merge' -p '{\"spec\":{\"engineState\":\"stop\"}}'",
            check=False,
        )
        run_command(f"kubectl delete chaosengine {name} -n {namespace}", check=False)
        logger.info(f"Aborted chaosengine/{name}")
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Abort all chaos experiments")
    parser.add_argument("--namespace", default=None, help="Namespace (default: app namespace)")
    parser.add_argument("--all-namespaces", action="store_true")
    args = parser.parse_args()

    config = get_config()
    profile = get_profile()

    if args.all_namespaces:
        if not profile.allow_abort_all:
            logger.error(f"CHAOS_ENV={profile.name} does not allow --all-namespaces abort")
            sys.exit(1)
        result = run_command(
            "kubectl get chaosengine -A -o jsonpath='{range .items[*]}{.metadata.namespace}{\" \"}{.metadata.name}{\"\\n\"}{end}'",
            check=False,
        )
        total = 0
        if result:
            for line in result.strip().splitlines():
                ns, name = line.split(maxsplit=1)
                try:
                    assert_namespace_allowed(ns)
                except Exception as exc:
                    logger.warning(f"Skipping {ns}/{name}: {exc}")
                    continue
                run_command(
                    f"kubectl delete chaosengine {name} -n {ns}",
                    check=False,
                )
                total += 1
        logger.info(f"Aborted {total} experiment(s) cluster-wide")
        sys.exit(0)

    namespace = args.namespace or config.app_namespace
    total = abort_namespace(namespace)
    logger.info(f"Aborted {total} experiment(s) in {namespace}")


if __name__ == "__main__":
    main()
