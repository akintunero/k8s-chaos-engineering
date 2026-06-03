#!/usr/bin/env bash
# Ensure a ChaosExperiment CR exists in the app namespace (required before ChaosEngine apply).
set -euo pipefail

EXPERIMENT="${1:?experiment name required}"
APP_NAMESPACE="${APP_NAMESPACE:-hello-world-app}"
LITMUS_VERSION="${LITMUS_VERSION:-3.28.1}"
TEMPLATE="templates/${EXPERIMENT}.yaml"

if kubectl get chaosexperiment "${EXPERIMENT}" -n "${APP_NAMESPACE}" >/dev/null 2>&1; then
  echo "==> ChaosExperiment ${EXPERIMENT} already present in ${APP_NAMESPACE}"
  exit 0
fi

helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/ 2>/dev/null || true
helm repo update litmuschaos >/dev/null

if ! helm search repo litmuschaos/kubernetes-chaos --version "${LITMUS_VERSION}" -l | grep -q 'litmuschaos/kubernetes-chaos'; then
  LITMUS_VERSION="$(helm search repo litmuschaos/kubernetes-chaos -l -o json | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["version"])')"
  echo "warning: kubernetes-chaos version fallback to ${LITMUS_VERSION}" >&2
fi

echo "==> Installing ChaosExperiment ${EXPERIMENT} from kubernetes-chaos ${LITMUS_VERSION}"
helm template "litmus-exp-${EXPERIMENT}" litmuschaos/kubernetes-chaos \
  --version "${LITMUS_VERSION}" \
  --namespace "${APP_NAMESPACE}" \
  --show-only "${TEMPLATE}" \
  | kubectl apply -f -
