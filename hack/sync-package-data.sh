#!/usr/bin/env bash
# Sync runtime YAML/assets into src/k8s_chaos/data for PyPI wheels.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${REPO_ROOT}/src/k8s_chaos/data"

echo "==> Syncing package data to ${DEST}"
rm -rf "${DEST}"
mkdir -p "${DEST}"

cp -R "${REPO_ROOT}/experiments" "${DEST}/"
cp -R "${REPO_ROOT}/config" "${DEST}/"
mkdir -p "${DEST}/workflows"
cp -R "${REPO_ROOT}/workflows/gameday" "${DEST}/workflows/"
mkdir -p "${DEST}/examples"
cp -R "${REPO_ROOT}/examples/quickstart" "${DEST}/examples/quickstart"

# Optional: include plugins config reference
mkdir -p "${REPO_ROOT}/plugins" 2>/dev/null || true

echo "==> Package data synced"
count="$(find "${DEST}" -type f | wc -l | tr -d ' ')"
echo "files: ${count}"
