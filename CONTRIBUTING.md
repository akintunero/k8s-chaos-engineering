# Contributing to K8s Chaos Engineering

Thank you for contributing. This project is a **LitmusChaos quickstart kit**—curated experiments, automation, and docs for resilience testing on Kubernetes.

---

## Code of conduct

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## Development setup

```bash
git clone https://github.com/akintunero/k8s-chaos-engineering.git
cd k8s-chaos-engineering

# Tools: kubectl, helm, python3 3.9+
brew install kubectl helm   # macOS example

# Start a cluster (pick one)
minikube start
# or: kind create cluster

# Verify environment
make doctor

# Install Python deps
make install   # removes stale egg-info, syncs data, editable install
# Pre-tag PyPI gate: make pypi-ready

# Golden path (installs Litmus + app + experiment + report)
make quickstart
```

Supported versions: [docs/version-matrix.md](docs/version-matrix.md).

---

## Running tests

```bash
make install   # once per clone
pytest tests/ -v
```

Before a PR:

```bash
make doctor
make validate-manifests
pytest tests/ -v
make helm-lint
```

Sign commits with DCO: `git commit -s -m "message"` (see [DCO.md](DCO.md)).

### Releases

Maintainers cut releases by pushing a tag `vMAJOR.MINOR.PATCH` (see [GOVERNANCE.md](GOVERNANCE.md)). This triggers the release workflow (Helm chart + SBOM).

### CI overview

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Orchestrates all checks |
| `test.yml` | Python unit tests |
| `manifests.yml` | Helm lint, kubeconform, kustomize |
| `e2e-kind.yml` | Full quickstart on KinD |
| `backend-ci.yml` | FastAPI import smoke test |
| `release.yml` | Artifacts on version tags |

### Safety and web

```bash
make preflight
make abort
make web-up    # optional UI
```

See [docs/safety.md](docs/safety.md).

### GameDay and SLO reports

```bash
make gameday-list
make gameday GAMEDAY=quickstart
make slo-report EXPERIMENT=pod-delete
```

See [docs/gameday.md](docs/gameday.md) and [docs/slo-reporting.md](docs/slo-reporting.md).

---

## Pull requests

1. Fork and create a feature branch (for example `feature/pod-delete-catalog-entry`).
2. Keep changes focused; match existing style.
3. Update docs/README if behavior changes.
4. Add or update tests for script changes.
5. Open a PR with a clear summary and test plan.

---

## Where to contribute

| Area | Path |
|------|------|
| Golden path manifests | `examples/quickstart/` |
| Experiments | `experiments/` + `experiments/catalog.yaml` |
| CLI / automation | `src/k8s_chaos/` (`k8s-chaos` entrypoint; `scripts/` shims) |
| Docs | `docs/`, `Readme.md` |
| CI | `.github/workflows/` |

Legacy directories (`manifests/`, `deployments/`) are not the default install path—avoid adding new features there.

---

## Code style

- Python: `black`, `isort`, `flake8` (see `[project.optional-dependencies]` dev in `pyproject.toml`)
- Meaningful names; comments only for non-obvious logic
- Tests for new behavior in `src/k8s_chaos/` (import as `k8s_chaos`)

---

## Getting help

- [LitmusChaos docs](https://docs.litmuschaos.io/)
- [Litmus Slack](https://slack.litmuschaos.io/)
- Open a GitHub issue with `kubectl version`, cluster provider, and steps to reproduce

---

## Maintainers

**Olúmáyòwá Akinkuehinmi** — [@akintunero](https://github.com/akintunero) — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)

See [MAINTAINERS.md](MAINTAINERS.md) for roles and contact.

---

## License

Contributions are licensed under [Apache-2.0](LICENSE).
