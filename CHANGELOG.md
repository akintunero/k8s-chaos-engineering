# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- CLI: add `k8s-chaos preflight --skip-app` and `--skip-litmus` (used by quickstart after app deploy)
- E2E KinD: pin `litmus-core`/`kubernetes-chaos` to 3.28.1 (latest published); install ChaosExperiment via `helm template` (hub URLs unavailable)
- CI: lint/security/backend/e2e workflows use `pip install -e .` and `src/k8s_chaos`; KinD quickstart uses `k8s-chaos` CLI
- Backend CI: add `web/backend/requirements.txt`, install `.[web]`, import `k8s_chaos.utils` in FastAPI app
- Lint: Black-format `src/k8s_chaos` with `--target-version py311`; fix CLI import; pin Black in `pyproject.toml`
- Frontend: stop ignoring `web/frontend/index.html` (was excluded by global `*.html` in `.gitignore`)
- Frontend: add `index.html`, Vite env types, `npm run lint` (tsc), and TypeScript fixes for production build

## [0.2.0] - 2026-06-02

### Added

- PyPI package (`k8s-chaos-engineering`), `k8s-chaos` CLI, bundled experiment/config assets, and publish workflow
- Golden path: `examples/quickstart/`, `make quickstart`, `hack/quickstart.sh`, `scripts/doctor.py`
- Experiment catalog, PASS/FAIL quickstart reports, and `docs/version-matrix.md`
- GameDay workflows (`workflows/gameday/`, `make gameday`) with optional notifications
- SLO probes in catalog, enhanced JSON reports, optional Prometheus integration
- Blast-radius profiles, preflight checks, experiment abort, and `docs/safety.md`
- Governance files (`GOVERNANCE.md`, `MAINTAINERS.md`, `ADOPTERS.md`, `DCO.md`, `CODEOWNERS`, Renovate)
- Release and SBOM workflows; manifest CI (Helm lint, kubeconform, Kustomize) and KinD e2e
- GitOps examples (`examples/gitops/`, `experiments/kustomization.yaml`) and `docs/gitops.md`
- Multi-cluster config and `k8s-chaos clusters` commands
- Unified CLI (`pyproject.toml`), GitHub Action v2, API v1, plugin hooks
- Experimental web UI stack (`make web-up`), API key and CORS configuration
- GitHub issue and PR templates

### Changed

- README repositioned as a Litmus quickstart kit (not a standalone chaos platform)
- Default app manifests path set to `examples/quickstart`
- Helm `values.yaml` aligned with deployment templates
- CLI and library code moved under `src/k8s_chaos/`; `scripts/` kept as thin shims

### Fixed

- Clear errors when `kubectl`/`helm` are missing; `make install` removes stale `scripts/*.egg-info`
- Pre-release gate (`make pypi-ready`) and documented PyPI vs source install paths
- Documentation aligned across CONTRIBUTING, scripts README, adopters, roadmap, and legacy guides (no placeholder contact or image names)

## [0.1.0] - 2025-03-30

### Added

- Initial LitmusChaos-oriented repo: Minikube quickstart, sample Flask app, basic experiment templates
- MongoDB deployment with authentication
- Core documentation, contribution guidelines, issue templates, and roadmap

### Changed

- MongoDB resource limits and authentication configuration
- README and setup documentation improvements

### Fixed

- MongoDB connection and resource allocation issues
- Port-forward configuration for local development
