#!/usr/bin/env bash
# Golden-path quickstart: prerequisites → Litmus → sample app → pod-delete → report
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SKIP_LITMUS="${SKIP_LITMUS:-0}"
SKIP_CHAOS="${SKIP_CHAOS:-0}"
EXPERIMENT="${EXPERIMENT:-pod-delete}"
LITMUS_NAMESPACE="${LITMUS_NAMESPACE:-litmus}"

export PYTHONPATH="${REPO_ROOT}/scripts:${PYTHONPATH:-}"
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

python3 -m pip install -q -r scripts/requirements.txt

echo "==> Running doctor (tools + cluster)"
python3 scripts/doctor.py

if [[ "${SKIP_LITMUS}" != "1" ]]; then
  if ! kubectl get namespace "${LITMUS_NAMESPACE}" >/dev/null 2>&1; then
    echo "==> Installing LitmusChaos in namespace ${LITMUS_NAMESPACE}"
    helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/ 2>/dev/null || true
    helm repo update
    helm upgrade --install litmus litmuschaos/litmus \
      --namespace "${LITMUS_NAMESPACE}" \
      --create-namespace \
      --wait \
      --timeout 10m
  else
    echo "==> Litmus namespace ${LITMUS_NAMESPACE} already exists (skipping install)"
  fi
fi

echo "==> Deploying quickstart application"
kubectl apply -k examples/quickstart
kubectl wait --for=condition=available deployment/flask-app \
  -n hello-world-app --timeout=180s

if [[ "${SKIP_CHAOS}" != "1" ]]; then
  echo "==> Pre-flight (CHAOS_ENV=${CHAOS_ENV})"
  python3 scripts/preflight.py

  echo "==> Running experiment: ${EXPERIMENT}"
  SKIP_PREFLIGHT=1 python3 scripts/chaos-runner.py run "${EXPERIMENT}"

  chaos_duration="${CHAOS_DURATION:-45}"
  echo "==> Waiting ${chaos_duration}s for chaos to complete..."
  sleep "${chaos_duration}"

  echo "==> Generating report"
  python3 scripts/quickstart_report.py --experiment "${EXPERIMENT}"
fi

echo ""
echo "Quickstart complete."
echo "  App:    kubectl get pods -n hello-world-app"
echo "  Litmus: kubectl get pods -n ${LITMUS_NAMESPACE}"
echo "  Stop:   python3 scripts/chaos-runner.py stop ${EXPERIMENT}"
