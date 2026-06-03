#!/usr/bin/env python3
"""
Generate a pass/fail experiment report with SLO probe evaluation.
"""

from __future__ import annotations

import argparse
import sys

from k8s_chaos.utils import get_config, get_logger
from k8s_chaos.utils.catalog import (
    get_experiment_meta,
    get_quickstart_settings,
    load_catalog,
    repo_root,
)
from k8s_chaos.utils.reporting import print_experiment_summary, write_report
from k8s_chaos.utils.slo import build_report_payload, evaluate_experiment_slo

logger = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chaos experiment SLO report")
    parser.add_argument("--experiment", default="pod-delete")
    parser.add_argument("--namespace", default=None)
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--recovery-timeout", type=int, default=None)
    args = parser.parse_args()

    config = get_config()
    root = repo_root()
    catalog = load_catalog()
    quickstart = get_quickstart_settings(catalog)

    namespace = args.namespace or quickstart.get("namespace", config.app_namespace)
    deployment = quickstart.get("deployment", "flask-app")
    expected = int(quickstart.get("expected_replicas", 3))
    timeout = args.recovery_timeout or int(quickstart.get("recovery_timeout_seconds", 120))

    meta = get_experiment_meta(catalog, args.experiment)
    evaluation = evaluate_experiment_slo(
        args.experiment,
        namespace=namespace,
        deployment=deployment,
        expected_replicas=expected,
        recovery_timeout=timeout,
        experiment_meta=meta,
    )

    report = build_report_payload(
        evaluation,
        namespace=namespace,
        deployment=deployment,
        report_type="experiment",
    )
    report_path = write_report(report, root / args.output_dir, basename="latest")
    print_experiment_summary(report, report_path)

    if report["verdict"] != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
