#!/usr/bin/env bash
# Ensure a ChaosExperiment CR exists in the app namespace (required before ChaosEngine apply).
set -euo pipefail

EXPERIMENT="${1:?experiment name required}"
APP_NAMESPACE="${APP_NAMESPACE:-hello-world-app}"
LITMUS_VERSION="${LITMUS_VERSION:-3.29.0}"

if kubectl get chaosexperiment "${EXPERIMENT}" -n "${APP_NAMESPACE}" >/dev/null 2>&1; then
  echo "==> ChaosExperiment ${EXPERIMENT} already present in ${APP_NAMESPACE}"
  exit 0
fi

hub_url="https://hub.litmuschaos.io/api/chaos/${LITMUS_VERSION}?file=charts/generic/${EXPERIMENT}/experiment.yaml"
echo "==> Installing ChaosExperiment ${EXPERIMENT} from Litmus hub (${LITMUS_VERSION})"
kubectl apply -f "${hub_url}" -n "${APP_NAMESPACE}"
