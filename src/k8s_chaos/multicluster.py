#!/usr/bin/env python3
"""
Multi-cluster experiment and GameDay execution with guardrails.
"""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from k8s_chaos.utils import get_config, get_logger
from k8s_chaos.utils.catalog import get_experiment_meta, get_quickstart_settings, load_catalog, repo_root
from k8s_chaos.utils.clusters import (
    apply_cluster_env,
    assert_experiment_allowed_on_cluster,
    cluster_context,
    get_cluster,
    resolve_clusters,
)
from k8s_chaos.utils.reporting import write_report
from k8s_chaos.utils.slo import evaluate_experiment_slo

logger = get_logger(__name__)


def _load_chaos_runner():
    from k8s_chaos import chaos_runner

    return chaos_runner


def _run_experiment_on_cluster(cluster_name: str, experiment: str) -> Dict[str, Any]:
    cluster = get_cluster(cluster_name)
    assert_experiment_allowed_on_cluster(cluster, experiment)
    catalog = load_catalog()
    quickstart = get_quickstart_settings(catalog)
    config = get_config()

    with cluster_context(cluster.context):
        for key, val in apply_cluster_env(cluster).items():
            os.environ[key] = val
        os.environ["SKIP_PREFLIGHT"] = "1"
        mod = _load_chaos_runner()
        mod.run_experiment(experiment, cluster.default_namespace)
        meta = get_experiment_meta(catalog, experiment)
        evaluation = evaluate_experiment_slo(
            experiment,
            namespace=cluster.default_namespace,
            deployment=quickstart.get("deployment", "flask-app"),
            expected_replicas=int(quickstart.get("expected_replicas", 3)),
            recovery_timeout=int(quickstart.get("recovery_timeout_seconds", 120)),
            experiment_meta=meta,
        )
        mod.stop_experiment(experiment, cluster.default_namespace)
        return {
            "cluster": cluster.name,
            "context": cluster.context,
            "chaos_env": cluster.chaos_env,
            "experiment": experiment,
            **evaluation.to_dict(),
        }


def run_experiment_on_clusters(
    experiment: str,
    cluster_names: List[str],
    *,
    allow_prod: bool = False,
) -> List[Dict[str, Any]]:
    names = resolve_clusters(cluster_names, allow_prod=allow_prod)
    results = []
    for name in names:
        logger.info("Experiment %s on cluster %s", experiment, name)
        try:
            results.append(_run_experiment_on_cluster(name, experiment))
        except Exception as exc:
            results.append(
                {"cluster": name, "verdict": "FAIL", "experiment": experiment, "error": str(exc)}
            )
    return results


def run_gameday_on_clusters(
    workflow: str,
    cluster_names: List[str],
    *,
    allow_prod: bool = False,
) -> List[Dict[str, Any]]:
    from k8s_chaos.gameday import execute_gameday

    names = resolve_clusters(cluster_names, allow_prod=allow_prod)
    results: List[Dict[str, Any]] = []
    for name in names:
        cluster = get_cluster(name)
        logger.info("GameDay %s on cluster %s", workflow, name)
        try:
            with cluster_context(cluster.context):
                os.environ.update(apply_cluster_env(cluster))
                report = execute_gameday(workflow, skip_preflight=False)
                report["cluster"] = cluster.name
                report["context"] = cluster.context
                results.append(report)
        except Exception as exc:
            results.append({"cluster": name, "verdict": "FAIL", "error": str(exc)})

    aggregate = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_type": "multicluster_gameday",
        "gameday": workflow,
        "verdict": "PASS" if all(r.get("verdict") == "PASS" for r in results) else "FAIL",
        "clusters": results,
    }
    write_report(aggregate, repo_root() / "reports", basename=f"multicluster-{workflow}")
    return results
