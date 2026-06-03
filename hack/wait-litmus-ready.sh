#!/usr/bin/env bash
# Wait for LitmusChaos CRDs and control-plane pods after helm install.
set -euo pipefail

NAMESPACE="${LITMUS_NAMESPACE:-litmus}"
CRD_TIMEOUT="${LITMUS_CRD_TIMEOUT:-300}"
POD_TIMEOUT="${LITMUS_POD_TIMEOUT:-300}"
LITMUS_MODE="${LITMUS_MODE:-core}"

echo "==> Waiting for ChaosEngine CRD (timeout ${CRD_TIMEOUT}s)"
deadline=$((SECONDS + CRD_TIMEOUT))
until kubectl get crd chaosengines.litmuschaos.io >/dev/null 2>&1; do
  if (( SECONDS >= deadline )); then
    echo "error: chaosengines.litmuschaos.io CRD not available" >&2
    echo "hint: use LITMUS_MODE=core (litmus-core chart), not litmus ChaosCenter alone" >&2
    kubectl get crd 2>/dev/null | grep -i litmus || true
    exit 1
  fi
  sleep 5
done
echo "==> ChaosEngine CRD is available"

if [[ "${LITMUS_MODE}" == "core" ]]; then
  echo "==> Waiting for litmus-core operator in ${NAMESPACE} (timeout ${POD_TIMEOUT}s)"
  if ! kubectl wait --for=condition=available deployment/litmus \
    -n "${NAMESPACE}" --timeout="${POD_TIMEOUT}s" 2>/dev/null; then
    if ! kubectl wait --for=condition=available deployment \
      -l "app=litmus" -n "${NAMESPACE}" --timeout=60s 2>/dev/null; then
      echo "warning: litmus-core deployment not ready; pod status:"
      kubectl get pods -n "${NAMESPACE}" -o wide || true
      not_ready="$(kubectl get pods -n "${NAMESPACE}" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l | tr -d ' ')"
      if [[ "${not_ready}" != "0" ]]; then
        echo "error: Litmus operator pods not ready in ${NAMESPACE}" >&2
        exit 1
      fi
    fi
  fi
else
  echo "==> Waiting for pods in namespace ${NAMESPACE} (timeout ${POD_TIMEOUT}s)"
  if ! kubectl wait --for=condition=ready pod -n "${NAMESPACE}" --all --timeout="${POD_TIMEOUT}s" 2>/dev/null; then
    echo "warning: not all Litmus pods ready; continuing with pod status:"
    kubectl get pods -n "${NAMESPACE}" -o wide || true
    not_ready="$(kubectl get pods -n "${NAMESPACE}" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "${not_ready}" != "0" ]]; then
      echo "error: Litmus pods not ready in ${NAMESPACE}" >&2
      exit 1
    fi
  fi
fi

echo "==> LitmusChaos is ready"
