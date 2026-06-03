#!/usr/bin/env bash
# Wait for LitmusChaos CRDs and control-plane pods after helm install.
set -euo pipefail

NAMESPACE="${LITMUS_NAMESPACE:-litmus}"
CRD_TIMEOUT="${LITMUS_CRD_TIMEOUT:-180}"
POD_TIMEOUT="${LITMUS_POD_TIMEOUT:-300}"

echo "==> Waiting for ChaosEngine CRD (timeout ${CRD_TIMEOUT}s)"
deadline=$((SECONDS + CRD_TIMEOUT))
until kubectl get crd chaosengines.litmuschaos.io >/dev/null 2>&1; do
  if (( SECONDS >= deadline )); then
    echo "error: chaosengines.litmuschaos.io CRD not available" >&2
    kubectl get crd 2>/dev/null | grep -i litmus || true
    exit 1
  fi
  sleep 5
done

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

echo "==> LitmusChaos is ready"
