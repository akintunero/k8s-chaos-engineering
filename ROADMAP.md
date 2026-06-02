# Project roadmap

## Project milestones

| Milestone | Focus | Status |
|-----------|--------|--------|
| **1** | Truth and cleanup — README, Helm values, golden manifests, legacy docs | Done |
| **2** | Golden path — `make quickstart`, catalog, PASS/FAIL report, version matrix | Done |
| **3** | OSS hardening — governance, releases, SBOM, strict CI, Renovate | Done |
| **4** | Cloud-native CI and GitOps — KinD e2e, manifest validation, Argo CD and Flux examples | Done |
| **5** | Web UI — Docker Compose, API auth hooks, backend CI | Done |

## Product milestones

| Milestone | Focus | Status |
|-----------|--------|--------|
| **6** | Safety and governance — blast-radius profiles, preflight, abort | Done |
| **7** | GameDay orchestration — workflows with pass/fail criteria | Done |
| **8** | SLO-linked reports — Prometheus probes, hypothesis registry | Done |
| **9** | Integrations — CLI package, Action v2, API v1, plugins, notifications | Done |
| **10** | Multi-cluster (guarded) — cluster registry, fan-out runner | Done |
| **11** | AI and recommendations (rules-first) | Planned |

## Shipped: integrations and multi-cluster

- `pyproject.toml` + `k8s-chaos` CLI (`make install` / `pip install k8s-chaos-engineering`)
- Action v2: experiment and GameDay modes, report artifact upload
- API `/api/v1/*` — [docs/integrations.md](docs/integrations.md)
- Plugin registry: `config/plugins.yaml` — [docs/plugins.md](docs/plugins.md)
- Multi-cluster: `config/clusters.yaml`, `k8s-chaos clusters` — [docs/multicluster.md](docs/multicluster.md)

## Shipped: GameDay and SLO reporting

- `k8s-chaos gameday`, `workflows/gameday/quickstart.yaml`, `resilience-basics.yaml`
- `k8s_chaos.utils.slo` — deployment, pod ratio, optional Prometheus probes
- `k8s-chaos report` with SLO probe section in JSON reports
- Docs: [docs/gameday.md](docs/gameday.md), [docs/slo-reporting.md](docs/slo-reporting.md)

## Shipped: web UI and safety

- Web: `web/backend/Dockerfile`, `web/frontend/Dockerfile`, `docker compose`, optional `CHAOS_API_KEY`
- Safety: `config/blast-radius.yaml`, `k8s-chaos preflight`, `k8s-chaos abort`
- Docs: [docs/safety.md](docs/safety.md)

## Shipped: OSS and GitOps

- [GOVERNANCE.md](GOVERNANCE.md), [MAINTAINERS.md](MAINTAINERS.md), [ADOPTERS.md](ADOPTERS.md), [DCO.md](DCO.md)
- Release workflow (Helm chart + SBOM on tag `v*.*.*`)
- Weekly SBOM artifact workflow
- Strict CI: manifests validation, KinD e2e, Bandit `-ll`
- [examples/gitops/](examples/gitops/) + [docs/gitops.md](docs/gitops.md)
- [renovate.json](renovate.json) for dependency updates

## Experiment catalog (complete)

- [x] Core infrastructure — Litmus, sample app, monitoring samples
- [x] Basic experiments — pod delete, CPU, memory, network latency
- [x] Advanced experiments — partition, disk, custom, multi-cluster
- [x] Monitoring samples — Prometheus, Grafana, alerts

Legacy experiment walkthrough: [docs/phase2-phase3-guide.md](docs/phase2-phase3-guide.md) (superseded by catalog + GameDay docs).

## How to contribute

See [CONTRIBUTING.md](CONTRIBUTING.md). Run `make doctor`, `make validate-manifests`, and `pytest tests/ -v` before opening a PR.

Maintainer: **Olúmáyòwá Akinkuehinmi** — [akintunero101@gmail.com](mailto:akintunero101@gmail.com)
