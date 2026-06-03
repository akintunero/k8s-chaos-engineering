#!/usr/bin/env bash
# Install Litmus for ChaosEngine-based experiments (litmus-core) or ChaosCenter UI (litmus).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="${LITMUS_NAMESPACE:-litmus}"
LITMUS_VERSION="${LITMUS_VERSION:-3.29.0}"
# core = chaos-operator + ChaosEngine CRDs (golden path). center = ChaosCenter portal only.
LITMUS_MODE="${LITMUS_MODE:-core}"

helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/ 2>/dev/null || true
helm repo update

if [[ "${LITMUS_MODE}" == "center" ]]; then
  echo "==> Installing Litmus ChaosCenter (portal) in namespace ${NAMESPACE}"
  helm upgrade --install litmus litmuschaos/litmus \
    --namespace "${NAMESPACE}" \
    --create-namespace \
    --wait \
    --timeout 15m
else
  echo "==> Installing Litmus chaos operator (litmus-core ${LITMUS_VERSION}) in namespace ${NAMESPACE}"
  helm upgrade --install litmus litmuschaos/litmus-core \
    --namespace "${NAMESPACE}" \
    --create-namespace \
    --version "${LITMUS_VERSION}" \
    --wait \
    --timeout 10m
fi

"${REPO_ROOT}/hack/wait-litmus-ready.sh"
