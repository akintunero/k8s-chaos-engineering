"""Tests for multi-cluster registry."""

import os

import pytest

from k8s_chaos.utils.clusters import (
    ClusterProfile,
    get_cluster,
    list_clusters,
    resolve_clusters,
)
from k8s_chaos.utils.safety import SafetyError


def test_list_clusters_loads_local():
    clusters = list_clusters()
    names = {c.name for c in clusters}
    assert "local" in names


def test_get_cluster_unknown():
    with pytest.raises(SafetyError):
        get_cluster("does-not-exist")


def test_prod_cluster_disabled_by_default():
    names = {c.name for c in list_clusters()}
    assert "prod-primary" not in names


def test_resolve_unknown_cluster():
    with pytest.raises(SafetyError):
        resolve_clusters(["missing-cluster"])


def test_assert_empty_allowed_list():
    from k8s_chaos.utils.clusters import assert_experiment_allowed_on_cluster

    cluster = ClusterProfile(name="x", context="c", chaos_env="dev", allowed_experiments=[])
    assert_experiment_allowed_on_cluster(cluster, "pod-delete")
