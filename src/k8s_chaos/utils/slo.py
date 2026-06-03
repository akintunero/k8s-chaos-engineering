"""
SLO probe evaluation for chaos experiments (Kubernetes-native + optional Prometheus).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .catalog import adjust_probes_for_e2e
from .config import get_config
from .k8s import run_command
from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProbeResult:
    name: str
    type: str
    verdict: str
    message: str
    optional: bool = False
    value: Optional[float] = None
    threshold: Optional[float] = None
    elapsed_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "type": self.type,
            "verdict": self.verdict,
            "message": self.message,
            "optional": self.optional,
            "value": self.value,
            "threshold": self.threshold,
        }
        if self.elapsed_seconds is not None:
            data["elapsed_seconds"] = round(self.elapsed_seconds, 2)
        return data


@dataclass
class SloEvaluation:
    experiment: str
    hypothesis: Optional[str]
    probes: List[ProbeResult] = field(default_factory=list)
    recovery_seconds: float = 0.0
    engine_status: str = "unknown"

    @property
    def verdict(self) -> str:
        for probe in self.probes:
            if probe.verdict == "FAIL":
                return "FAIL"
        if any(p.verdict == "PASS" for p in self.probes):
            return "PASS"
        return "FAIL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment": self.experiment,
            "hypothesis": self.hypothesis,
            "verdict": self.verdict,
            "recovery_seconds": round(self.recovery_seconds, 2),
            "engine_status": self.engine_status,
            "probes": [p.to_dict() for p in self.probes],
        }


def _prometheus_enabled() -> bool:
    flag = os.getenv("PROMETHEUS_SLO_ENABLED", "false").lower()
    return flag in ("1", "true", "yes", "on")


def _prometheus_url() -> str:
    config = get_config()
    return os.getenv("PROMETHEUS_URL", config.prometheus_url).rstrip("/")


def deployment_ready(namespace: str, deployment: str) -> tuple[int, int]:
    ready = run_command(
        f"kubectl get deployment {deployment} -n {namespace} " "-o jsonpath='{.status.readyReplicas}'",
        check=False,
    )
    desired = run_command(
        f"kubectl get deployment {deployment} -n {namespace} " "-o jsonpath='{.spec.replicas}'",
        check=False,
    )
    ready_n = int(ready) if ready and ready.isdigit() else 0
    desired_n = int(desired) if desired and desired.isdigit() else 0
    return ready_n, desired_n


def wait_for_deployment_slo(
    namespace: str,
    deployment: str,
    min_ready: int,
    timeout: int,
    interval: int,
) -> tuple[bool, int, int, float]:
    start = time.time()
    while time.time() - start < timeout:
        ready_n, desired_n = deployment_ready(namespace, deployment)
        if ready_n >= min_ready and desired_n >= min_ready:
            return True, ready_n, desired_n, time.time() - start
        time.sleep(interval)
    ready_n, desired_n = deployment_ready(namespace, deployment)
    ok = ready_n >= min_ready
    return ok, ready_n, desired_n, time.time() - start


def pods_ready_fraction(namespace: str, label_selector: str) -> tuple[float, int, int]:
    raw = run_command(
        f"kubectl get pods -n {namespace} -l {label_selector} -o json",
        check=False,
    )
    if not raw:
        return 0.0, 0, 0
    data = json.loads(raw)
    items = data.get("items", [])
    if not items:
        return 0.0, 0, 0
    ready = 0
    for pod in items:
        conditions = pod.get("status", {}).get("conditions", [])
        if any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions):
            ready += 1
    return ready / len(items), ready, len(items)


def query_prometheus(promql: str) -> Optional[float]:
    if not _prometheus_enabled():
        return None
    base = _prometheus_url()
    query = urllib.parse.urlencode({"query": promql})
    url = f"{base}/api/v1/query?{query}"
    timeout = int(os.getenv("PROMETHEUS_TIMEOUT", "5"))
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec B310
            payload = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Prometheus query failed: %s", exc)
        return None

    if payload.get("status") != "success":
        return None
    result = payload.get("data", {}).get("result", [])
    if not result:
        return None
    value = result[0].get("value", [None, None])[1]
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare(value: float, threshold: float, operator: str) -> bool:
    ops = {
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "eq": lambda a, b: a == b,
    }
    fn = ops.get(operator, ops["lte"])
    return fn(value, threshold)


def run_probe(
    probe: Dict[str, Any],
    *,
    namespace: str,
    deployment: str,
    expected_replicas: int,
    recovery_timeout: int,
    interval: int,
) -> ProbeResult:
    name = probe.get("name", probe.get("type", "probe"))
    ptype = probe.get("type", "deployment_ready")
    optional = bool(probe.get("optional", False))

    if ptype == "deployment_ready":
        min_ready = int(probe.get("min_ready_replicas", expected_replicas))
        timeout = int(probe.get("max_recovery_seconds", recovery_timeout))
        ok, ready_n, desired_n, elapsed = wait_for_deployment_slo(namespace, deployment, min_ready, timeout, interval)
        return ProbeResult(
            name=name,
            type=ptype,
            verdict="PASS" if ok else "FAIL",
            message=f"deployment/{deployment} ready {ready_n}/{desired_n} (min {min_ready})",
            optional=optional,
            value=float(ready_n),
            threshold=float(min_ready),
            elapsed_seconds=elapsed,
        )

    if ptype == "pods_ready_ratio":
        selector = probe.get("label_selector", "app=flask-app")
        min_ratio = float(probe.get("min_ready_ratio", 1.0))
        fraction, ready, total = pods_ready_fraction(namespace, selector)
        ok = fraction >= min_ratio and total > 0
        return ProbeResult(
            name=name,
            type=ptype,
            verdict="PASS" if ok else "FAIL",
            message=f"pods ready {ready}/{total} ({fraction:.0%}, need {min_ratio:.0%})",
            optional=optional,
            value=fraction,
            threshold=min_ratio,
        )

    if ptype == "prometheus":
        if not _prometheus_enabled():
            return ProbeResult(
                name=name,
                type=ptype,
                verdict="SKIP",
                message="Prometheus SLO disabled (set PROMETHEUS_SLO_ENABLED=true)",
                optional=True,
            )
        promql = probe.get("query", "")
        threshold = float(probe.get("threshold", 0))
        operator = probe.get("operator", "lte")
        value = query_prometheus(promql)
        if value is None:
            return ProbeResult(
                name=name,
                type=ptype,
                verdict="SKIP" if optional else "FAIL",
                message=f"Prometheus unavailable or empty result for: {promql}",
                optional=optional,
            )
        ok = _compare(value, threshold, operator)
        return ProbeResult(
            name=name,
            type=ptype,
            verdict="PASS" if ok else "FAIL",
            message=f"query={promql} value={value} {operator} {threshold}",
            optional=optional,
            value=value,
            threshold=threshold,
        )

    return ProbeResult(
        name=name,
        type=ptype,
        verdict="SKIP",
        message=f"Unknown probe type: {ptype}",
        optional=True,
    )


def default_probes_for_experiment(
    experiment_meta: Dict[str, Any],
    expected_replicas: int,
    recovery_timeout: int,
) -> List[Dict[str, Any]]:
    if experiment_meta.get("slo"):
        return list(experiment_meta["slo"])
    return [
        {
            "name": "deployment_recovery",
            "type": "deployment_ready",
            "min_ready_replicas": expected_replicas,
            "max_recovery_seconds": recovery_timeout,
        },
        {
            "name": "pods_ready",
            "type": "pods_ready_ratio",
            "label_selector": "app=flask-app",
            "min_ready_ratio": 1.0,
        },
    ]


def evaluate_experiment_slo(
    experiment_name: str,
    *,
    namespace: str,
    deployment: str,
    expected_replicas: int,
    recovery_timeout: int,
    experiment_meta: Optional[Dict[str, Any]] = None,
    extra_probes: Optional[List[Dict[str, Any]]] = None,
) -> SloEvaluation:
    config = get_config()
    meta = experiment_meta or {}
    hypothesis = meta.get("hypothesis")
    probes_cfg = extra_probes or default_probes_for_experiment(meta, expected_replicas, recovery_timeout)
    probes_cfg = adjust_probes_for_e2e(probes_cfg, expected_replicas)

    evaluation = SloEvaluation(experiment=experiment_name, hypothesis=hypothesis)
    recovery_elapsed = 0.0

    for probe_cfg in probes_cfg:
        result = run_probe(
            probe_cfg,
            namespace=namespace,
            deployment=deployment,
            expected_replicas=expected_replicas,
            recovery_timeout=recovery_timeout,
            interval=config.check_interval,
        )
        evaluation.probes.append(result)
        if result.elapsed_seconds is not None:
            recovery_elapsed = max(recovery_elapsed, result.elapsed_seconds)

    evaluation.recovery_seconds = recovery_elapsed

    engine_status = run_command(
        f"kubectl get chaosengine {experiment_name} -n {namespace} " "-o jsonpath='{.status.engineStatus}'",
        check=False,
    )
    evaluation.engine_status = engine_status or "unknown"
    return evaluation


def build_report_payload(
    evaluation: SloEvaluation,
    *,
    namespace: str,
    deployment: str,
    report_type: str = "experiment",
    gameday_name: Optional[str] = None,
    steps: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_type": report_type,
        "verdict": evaluation.verdict if not steps else _steps_verdict(steps),
        "namespace": namespace,
        "deployment": deployment,
        "chaos_env": os.getenv("CHAOS_ENV", "dev"),
    }
    if gameday_name:
        payload["gameday"] = gameday_name
    if steps is not None:
        payload["steps"] = steps
    else:
        payload.update(evaluation.to_dict())
    return payload


def aggregate_steps_verdict(steps: List[Dict[str, Any]]) -> str:
    for step in steps:
        if step.get("verdict") == "FAIL":
            return "FAIL"
    if any(step.get("verdict") == "SKIP" for step in steps):
        if not any(step.get("verdict") == "PASS" for step in steps):
            return "SKIP"
    return "PASS"


def _steps_verdict(steps: List[Dict[str, Any]]) -> str:
    return aggregate_steps_verdict(steps)
