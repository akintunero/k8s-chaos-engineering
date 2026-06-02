#!/usr/bin/env bash
# Remove stale editable-install metadata under scripts/ that shadows the real package.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STALE="${REPO_ROOT}/scripts/k8s_chaos_engineering.egg-info"

if [[ -d "${STALE}" ]]; then
  echo "==> Removing stale ${STALE} (breaks pip install from repo root)"
  rm -rf "${STALE}"
fi
