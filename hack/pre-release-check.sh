#!/usr/bin/env bash
# Local gate before tagging a PyPI release.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

PYTHON="${PYTHON:-python3}"
shopt -s nullglob
WHEELS=( "${REPO_ROOT}"/dist/k8s_chaos_engineering-*.whl )
shopt -u nullglob
if [[ ${#WHEELS[@]} -eq 0 ]]; then
  echo "No wheel found in ${REPO_ROOT}/dist/" >&2
  exit 1
fi
WHEEL="${WHEELS[0]}"

echo "==> Dev install hygiene"
chmod +x hack/ensure-dev-install.sh hack/sync-package-data.sh
./hack/ensure-dev-install.sh

echo "==> Unit tests"
"${PYTHON}" -m pytest -q --no-cov

echo "==> Build and validate distribution"
make sync-package-data build-dist check-dist

echo "==> Wheel smoke test (clean venv)"
VENV="$(mktemp -d)/k8s-chaos-pre-release"
"${PYTHON}" -m venv "${VENV}"
# shellcheck disable=SC1091
source "${VENV}/bin/activate"
pip install -q "${WHEEL}"
k8s-chaos list >/dev/null
k8s-chaos --help >/dev/null
deactivate
rm -rf "$(dirname "${VENV}")"

echo "==> Pre-release checks passed"
