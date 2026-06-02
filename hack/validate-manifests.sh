#!/usr/bin/env bash
# Validate Kubernetes manifests and Helm chart without a live cluster.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Helm lint"
helm lint helm/

echo "==> Kustomize build (quickstart)"
kubectl kustomize examples/quickstart >/tmp/quickstart-rendered.yaml

if command -v kubeconform >/dev/null 2>&1; then
  echo "==> Kubeconform (quickstart)"
  kubeconform -summary -kubernetes-version 1.28.0 -ignore-missing-schemas /tmp/quickstart-rendered.yaml
else
  echo "skip: kubeconform not installed (optional locally)"
fi

echo "==> YAML syntax (experiments)"
python3 - <<'PY'
import sys
from pathlib import Path
import yaml

root = Path("experiments")
for path in sorted(root.glob("*.yaml")):
    if path.name == "catalog.yaml":
        continue
    with open(path, encoding="utf-8") as f:
        list(yaml.safe_load_all(f))
    print(f"  ok: {path}")
PY

echo "==> Manifest validation passed"
