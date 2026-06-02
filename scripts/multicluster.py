"""Backward-compatible module — use `k8s-chaos` subcommands for multicluster runs."""

from k8s_chaos.multicluster import (  # noqa: F401
    run_experiment_on_clusters,
    run_gameday_on_clusters,
)
