"""Tests for blast-radius safety utilities."""

import os

import pytest

from k8s_chaos.utils.safety import (
    SafetyError,
    assert_experiment_allowed,
    assert_namespace_allowed,
    get_profile,
    is_experiment_file,
)


def test_is_experiment_file():
    assert is_experiment_file("pod-delete") is True
    assert is_experiment_file("rbac") is False
    assert is_experiment_file("catalog") is False


def test_dev_profile_allows_pod_delete(monkeypatch):
    monkeypatch.delenv("CHAOS_ENV", raising=False)
    profile = get_profile()
    assert profile.name == "dev"
    assert_experiment_allowed("pod-delete", profile)


def test_prod_requires_confirm(monkeypatch):
    monkeypatch.setenv("CHAOS_ENV", "prod")
    monkeypatch.delenv("CHAOS_CONFIRM", raising=False)
    profile = get_profile()
    with pytest.raises(SafetyError):
        assert_experiment_allowed("pod-delete", profile, confirmed=False)


def test_prod_with_confirm(monkeypatch):
    monkeypatch.setenv("CHAOS_ENV", "prod")
    monkeypatch.setenv("CHAOS_CONFIRM", "yes")
    assert_experiment_allowed("pod-delete", get_profile())


def test_blocked_namespace(monkeypatch):
    monkeypatch.setenv("CHAOS_ENV", "dev")
    with pytest.raises(SafetyError):
        assert_namespace_allowed("kube-system", get_profile())


def test_staging_disallows_disk_stress(monkeypatch):
    monkeypatch.setenv("CHAOS_ENV", "staging")
    with pytest.raises(SafetyError):
        assert_experiment_allowed("disk-stress", get_profile())
