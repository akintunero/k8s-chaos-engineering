# PyPI distribution

Package: **[k8s-chaos-engineering](https://pypi.org/project/k8s-chaos-engineering/)** (CLI: `k8s-chaos`)

## Runtime requirements (not installed by pip)

| Requirement | Used for |
|-------------|----------|
| `kubectl` | Apply experiments, status, abort |
| `helm` | Litmus install, monitoring (optional) |
| Kubernetes cluster | All chaos / report / GameDay runs |
| `python3` 3.9+ | CLI only (bundled in the wheel) |

Offline-friendly commands (`k8s-chaos list`, `k8s-chaos gameday --list`) only need the packaged YAML.

After install, verify tooling:

```bash
k8s-chaos doctor
k8s-chaos doctor --full   # includes Litmus + quickstart app
```

## Install

```bash
pip install k8s-chaos-engineering
k8s-chaos doctor
k8s-chaos list
```

> Until the first GitHub Release is published, PyPI will not have the package. Use a [development install](#development-install) from a git clone instead.

## Development install

Always run from the **repository root** (not `scripts/`):

```bash
git clone https://github.com/akintunero/k8s-chaos-engineering.git
cd k8s-chaos-engineering
make install    # removes stale egg-info, syncs data, editable install
k8s-chaos doctor
```

Or manually:

```bash
./hack/ensure-dev-install.sh
./hack/sync-package-data.sh
pip install -e ".[dev]"
```

### Stale `scripts/k8s_chaos_engineering.egg-info`

If `pip install` reports the package location as `.../scripts` or `k8s-chaos` is missing from the active virtual environment:

```bash
rm -rf scripts/k8s_chaos_engineering.egg-info
./hack/ensure-dev-install.sh
pip install -e ".[dev]" --force-reinstall
```

`make install` runs `ensure-dev-install` automatically.

## Build locally

```bash
make sync-package-data
make build-dist
make check-dist
```

Test wheel in a clean venv (from `/tmp` or outside the repo to avoid path confusion):

```bash
cd /tmp
python3 -m venv k8s-chaos-test
source k8s-chaos-test/bin/activate
pip install /path/to/k8s-chaos-engineering/dist/k8s_chaos_engineering-*.whl
k8s-chaos list
```

## Pre-release gate

Before tagging:

```bash
make pypi-ready
```

Runs tests, `twine check`, and a wheel smoke install in a temporary venv.

## Publish

Publishing runs on **GitHub Release published** via `.github/workflows/publish-pypi.yml` (OIDC trusted publishing).

1. Run `make pypi-ready`
2. Bump version in `pyproject.toml` and `src/k8s_chaos/__init__.py`
3. Move `CHANGELOG.md` `[Unreleased]` → `[x.y.z] - date`
4. `./hack/sync-package-data.sh`
5. Commit, push, create tag `v0.2.0`
6. Publish GitHub Release from that tag

### First-time PyPI setup

Package maintainer: **Olúmáyòwá Akinkuehinmi** — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

1. Create account on https://pypi.org
2. Register project name `k8s-chaos-engineering` (check availability)
3. Configure trusted publisher on PyPI:
   - Owner: `akintunero` (or the GitHub org that owns the repository)
   - Repository: `k8s-chaos-engineering`
   - Workflow: `publish-pypi.yml`
   - Environment: `pypi`
4. Create matching GitHub environment **`pypi`**

### Custom data directory

```bash
export K8S_CHAOS_HOME=/path/to/checkout
k8s-chaos list
```

Bundled data lives in `k8s_chaos/data/` inside the wheel.
