#!/usr/bin/env bash
# Golden-path quickstart: prerequisites → Litmus → sample app → pod-delete → report
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SKIP_LITMUS="${SKIP_LITMUS:-0}"
SKIP_CHAOS="${SKIP_CHAOS:-0}"
EXPERIMENT="${EXPERIMENT:-pod-delete}"
LITMUS_NAMESPACE="${LITMUS_NAMESPACE:-litmus}"

export CHAOS_ENV="${CHAOS_ENV:-dev}"

echo "==> Chaos Engineering Quickstart"
echo "    Repository: ${REPO_ROOT}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "error: kubectl is required" >&2
  exit 1
fi
if ! command -v helm >/dev/null 2>&1; then
  echo "error: helm is required" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

chmod +x "${REPO_ROOT}/hack/ensure-dev-install.sh" "${REPO_ROOT}/hack/sync-package-data.sh"
"${REPO_ROOT}/hack/ensure-dev-install.sh"
"${REPO_ROOT}/hack/sync-package-data.sh"
python3 -m pip install -q -e .

echo "==> Running doctor (tools + cluster)"
k8s-chaos doctor

if [[ "${SKIP_LITMUS}" != "1" ]]; then
  if ! kubectl get namespace "${LITMUS_NAMESPACE}" >/dev/null 2>&1; then
    echo "==> Installing LitmusChaos in namespace ${LITMUS_NAMESPACE}"
    helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/ 2>/dev/null || true
    helm repo update
    helm upgrade --install litmus litmuschaos/litmus \
      --namespace "${LITMUS_NAMESPACE}" \
      --create-namespace \
      --wait \
      --timeout 15m
  else
    echo "==> Litmus namespace ${LITMUS_NAMESPACE} already exists (skipping install)"
  fi
fi

echo "==> Deploying quickstart application"
kubectl apply -k examples/quickstart
if ! kubectl wait --for=condition=available deployment/flask-app \
  -n hello-world-app --timeout=300s; then
  echo "error: quickstart app did not become ready" >&2
  kubectl get pods -n hello-world-app -o wide || true
  exit 1
fi

if [[ "${SKIP_CHAOS}" != "1" ]]; then
  echo "==> Pre-flight (CHAOS_ENV=${CHAOS_ENV})"
  k8s-chaos preflight

  echo "==> Running experiment: ${EXPERIMENT}"
  SKIP_PREFLIGHT=1 k8s-chaos run "${EXPERIMENT}"

  chaos_duration="${CHAOS_DURATION:-45}"
  echo "==> Waiting ${chaos_duration}s for chaos to complete..."
  sleep "${chaos_duration}"

  echo "==> Generating report"
  k8s-chaos report "${EXPERIMENT}"
fi

echo ""
echo "Quickstart complete."
echo "  App:    kubectl get pods -n hello-world-app"
echo "  Litmus: kubectl get pods -n ${LITMUS_NAMESPACE}"
echo "  Stop:   k8s-chaos abort"
