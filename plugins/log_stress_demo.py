"""Example chaos experiment plugin."""

from __future__ import annotations

from typing import Any, Dict


def generate_manifest(params: Dict[str, Any]) -> str:
    namespace = params.get("namespace", "hello-world-app")
    duration = params.get("duration", 30)
    return f"""apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: plugin-log-stress
  namespace: {namespace}
spec:
  appinfo:
    appns: {namespace}
    applabel: "app=flask-app"
    appkind: deployment
  engineState: "active"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "{duration}"
"""
