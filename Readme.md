# Kubernetes Chaos Engineering (Litmus quickstart kit)

[![CI](https://github.com/akintunero/k8s-chaos-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/akintunero/k8s-chaos-engineering/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/akintunero/k8s-chaos-engineering)](LICENSE)
[![LitmusChaos](https://img.shields.io/badge/LitmusChaos-experiments-orange)](https://litmuschaos.io)

**Curated LitmusChaos experiments, guardrails, and automation** for teams who want a working chaos smoke test on Kubernetes—not another control plane.

> Clone → one command → pod-delete experiment → **PASS/FAIL report** in ~15 minutes.

---

## What this project is

| You get | You do not get |
|--------|----------------|
| Ready-to-run `ChaosEngine` manifests | A replacement for [Litmus](https://litmuschaos.io) |
| Python CLI (`chaos-runner`, reports, scheduler) | Managed SaaS chaos |
| Quickstart app + RBAC golden path | Production AI-driven chaos (see `chaos/` — experimental) |
| CI-friendly GitHub Action | Full multi-cloud operator |

Built on **LitmusChaos**. We add opinionated templates, quickstart automation, and reporting.

---

## Quickstart (recommended)

**Prerequisites:** Kubernetes cluster, `kubectl`, `helm`, `python3` 3.9+. See [docs/version-matrix.md](docs/version-matrix.md).

```bash
# After the first PyPI release (see docs/pypi.md):
pip install k8s-chaos-engineering
k8s-chaos doctor

# From source (works before PyPI publish):
git clone https://github.com/akintunero/k8s-chaos-engineering.git
cd k8s-chaos-engineering && make install
k8s-chaos doctor

make quickstart
```

The Python package ships manifests and automation only; **`kubectl` and `helm` must be installed separately**. Cluster commands fail fast with install hints if they are missing.

Publishing, local wheels, and pre-release checks: [docs/pypi.md](docs/pypi.md) (`make pypi-ready`).

This will:

1. Verify tools and cluster connectivity (`doctor`)
2. Install LitmusChaos (if missing)
3. Deploy the sample app from `examples/quickstart/`
4. Run the **pod-delete** experiment
5. Write `reports/latest.json` with a **PASS/FAIL** verdict

**Options:**

```bash
SKIP_LITMUS=1 make quickstart    # cluster already has Litmus
SKIP_CHAOS=1 make quickstart     # deploy app only
./hack/quickstart.sh             # same as make quickstart
```

---

## Manual steps

### Install LitmusChaos

```bash
make install-litmus
kubectl get pods -n litmus
```

### Deploy the sample application

```bash
make deploy-app
kubectl get pods -n hello-world-app -l app=flask-app
```

### Run an experiment

```bash
make run-experiment EXPERIMENT=pod-delete
make quickstart-report EXPERIMENT=pod-delete
```

### Stop an experiment

```bash
make stop-experiment EXPERIMENT=pod-delete
```

---

## Experiment catalog

| Phase | Experiments |
|-------|-------------|
| 2 | `pod-delete`, `cpu-hog`, `memory-hog`, `network-latency` |
| 3 | `network-partition`, `disk-stress`, `custom-chaos`, `multi-cluster-chaos` |

Metadata: [`experiments/catalog.yaml`](experiments/catalog.yaml)

```bash
make list-experiments
python3 scripts/advanced-chaos-runner.py list
```

---

## Automation

```bash
make doctor              # kubectl, helm, cluster
make list-experiments
make run-experiment EXPERIMENT=cpu-hog
make cleanup
```

Interactive setup (Litmus + app + optional monitoring):

```bash
make setup
```

---

## CI & GitOps

| Capability | Location |
|------------|----------|
| Main CI (tests, lint, security, manifests, KinD e2e) | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Manifest validation (Helm + kubeconform) | `make validate-manifests` |
| KinD e2e quickstart | [`.github/workflows/e2e-kind.yml`](.github/workflows/e2e-kind.yml) |
| Chaos smoke test Action | [`.github/actions/chaos-test`](.github/actions/chaos-test) |
| Releases + SBOM | Tag `v*.*.*` → [release workflow](.github/workflows/release.yml) |
| Argo CD / Flux examples | [`examples/gitops/`](examples/gitops/) · [docs/gitops.md](docs/gitops.md) |

```yaml
# Example: chaos regression in a GitHub Actions workflow (cluster required)
- uses: ./.github/actions/chaos-test
  with:
    experiment: pod-delete
```

---

## Safety (blast-radius)

```bash
export CHAOS_ENV=dev          # dev | staging | prod
make preflight                # cluster, Litmus, app, no active chaos
make run-experiment EXPERIMENT=pod-delete
make abort                    # emergency stop
```

Profiles: [`config/blast-radius.yaml`](config/blast-radius.yaml) · [docs/safety.md](docs/safety.md)

## Integrations & multi-cluster

```bash
pip install -e .
k8s-chaos gameday quickstart
k8s-chaos clusters local --experiment pod-delete
```

- [docs/integrations.md](docs/integrations.md) — CLI, Action v2, API v1  
- [docs/multicluster.md](docs/multicluster.md) — cluster registry  

## GameDay & SLO reports

```bash
make gameday GAMEDAY=quickstart     # ordered steps + PASS/FAIL per step
make slo-report EXPERIMENT=pod-delete
```

- [docs/gameday.md](docs/gameday.md) — workflow orchestration  
- [docs/slo-reporting.md](docs/slo-reporting.md) — probes, Prometheus, hypotheses  

## Web UI (beta)

```bash
make web-up    # Docker Compose — http://localhost:3000
```

See [`web/README.md`](web/README.md).

---

## Project layout

```
k8s-chaos-engineering/
├── examples/quickstart/   # Golden path manifests (use this)
├── experiments/           # Litmus ChaosEngine YAML + catalog.yaml
├── examples/gitops/       # Argo CD & Flux samples
├── src/k8s_chaos/         # Python package (k8s-chaos CLI)
├── scripts/               # backward-compatible shims
├── hack/quickstart.sh     # One-command golden path
├── helm/                  # Optional demo chart
├── monitoring/            # Prometheus/Grafana extras
├── manifests/             # Legacy (see manifests/README.md)
├── deployments/           # Legacy snippets (see deployments/README.md)
├── web/                   # Experimental UI
└── docs/                  # Architecture, version matrix, guides
```

---

## Roadmap

Shipped capabilities and planned work are tracked in [ROADMAP.md](ROADMAP.md).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please run `make doctor` and tests before opening a PR.

---

## Contact

| | |
|---|---|
| **Maintainer** | Olúmáyòwá Akinkuehinmi ([@akintunero](https://github.com/akintunero)) |
| **Email** | [akintunero101@gmail.com](mailto:akintunero101@gmail.com) |

Governance: [MAINTAINERS.md](MAINTAINERS.md) · [GOVERNANCE.md](GOVERNANCE.md) · Security: [SECURITY.md](SECURITY.md)

---

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).
