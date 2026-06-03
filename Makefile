.PHONY: help setup quickstart doctor install-litmus deploy-app setup-monitoring run-experiment stop-experiment cleanup list-experiments phase2 phase3 workflow report

REPO_ROOT := $(shell pwd)
export PYTHONPATH := $(REPO_ROOT)/src:$(REPO_ROOT)/scripts:$(PYTHONPATH)
PYTHON ?= python3

help: ## Show this help message
	@echo "Kubernetes Chaos Engineering — Litmus quickstart kit"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

quickstart: ## Golden path: Litmus + app + pod-delete + PASS/FAIL report
	chmod +x hack/quickstart.sh
	./hack/quickstart.sh

doctor: ## Check kubectl, helm, cluster (use doctor-full for Litmus/app)
	python3 scripts/doctor.py

doctor-full: ## Doctor including Litmus and quickstart app
	python3 scripts/doctor.py --full

setup: ## Interactive setup (Litmus, app, monitoring)
	python3 scripts/setup.py

install-litmus: ## Install Litmus chaos operator (ChaosEngine CRDs)
	chmod +x hack/install-litmus.sh hack/wait-litmus-ready.sh
	./hack/install-litmus.sh

deploy-app: ## Deploy quickstart sample application
	kubectl apply -k examples/quickstart
	kubectl wait --for=condition=available deployment/flask-app -n hello-world-app --timeout=180s

setup-monitoring: ## Setup Prometheus and Grafana monitoring
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
	helm repo update
	helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

run-experiment: ## Run chaos experiment (make run-experiment EXPERIMENT=pod-delete)
	@if [ -z "$(EXPERIMENT)" ]; then \
		echo "Usage: make run-experiment EXPERIMENT=pod-delete"; \
		python3 scripts/chaos-runner.py list; \
	else \
		python3 scripts/chaos-runner.py run $(EXPERIMENT); \
	fi

stop-experiment: ## Stop chaos experiment (make stop-experiment EXPERIMENT=pod-delete)
	@if [ -z "$(EXPERIMENT)" ]; then \
		echo "Usage: make stop-experiment EXPERIMENT=pod-delete"; \
	else \
		python3 scripts/chaos-runner.py stop $(EXPERIMENT); \
	fi

quickstart-report: ## Generate report for an experiment (default pod-delete)
	python3 scripts/quickstart_report.py --experiment $(or $(EXPERIMENT),pod-delete)

cleanup: ## Clean up all chaos experiments
	python3 scripts/chaos-runner.py cleanup

list-experiments: ## List available chaos experiments
	python3 scripts/chaos-runner.py list

check-status: ## Check status of running experiments
	python3 scripts/chaos-runner.py running

port-forward-grafana: ## Port forward Grafana dashboard
	kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

port-forward-app: ## Port forward quickstart application
	kubectl port-forward svc/flask-app-service -n hello-world-app 8080:80

phase2: ## Run all Phase 2 experiments
	python3 scripts/advanced-chaos-runner.py phase2

phase3: ## Run all Phase 3 experiments
	python3 scripts/advanced-chaos-runner.py phase3

workflow: ## Run comprehensive chaos workflow
	python3 scripts/advanced-chaos-runner.py workflow

report: ## Generate chaos experiment report (advanced runner)
	python3 scripts/advanced-chaos-runner.py report

list-phases: ## List experiments by phase
	python3 scripts/advanced-chaos-runner.py list

setup-monitoring-advanced: ## Apply chaos dashboards and alerts
	kubectl apply -f monitoring/chaos-dashboard.yaml
	kubectl apply -f monitoring/chaos-alerts.yaml

helm-lint: ## Lint the sample Helm chart
	helm lint helm/

validate-manifests: ## Validate Helm/Kustomize/YAML (no cluster required)
	chmod +x hack/validate-manifests.sh
	./hack/validate-manifests.sh

kind-e2e: ## Run quickstart on existing KinD cluster (create cluster first)
	./hack/quickstart.sh

preflight: ## Run safety pre-flight checks
	python3 scripts/preflight.py

abort: ## Abort all chaos engines in the app namespace
	python3 scripts/chaos-runner.py abort

web-up: ## Start web UI via Docker Compose (requires kubeconfig)
	cd web && docker compose up --build

web-down: ## Stop web UI stack
	cd web && docker compose down

sync-package-data: ## Copy YAML assets into src/k8s_chaos/data for wheels
	chmod +x hack/sync-package-data.sh
	./hack/sync-package-data.sh

ensure-dev-install: ## Remove stale scripts/*.egg-info before pip install
	chmod +x hack/ensure-dev-install.sh
	./hack/ensure-dev-install.sh

install: ensure-dev-install sync-package-data ## Install CLI locally (editable)
	$(PYTHON) -m pip install -e ".[dev]"

format: ## Format Python sources (Black + isort, py311)
	isort src/k8s_chaos
	black --target-version py311 src/k8s_chaos

pypi-ready: ## Run tests, build wheel, and smoke-install (pre-tag gate)
	chmod +x hack/pre-release-check.sh
	./hack/pre-release-check.sh

install-cli: install ## Alias for install

build-dist: sync-package-data ## Build PyPI wheel and sdist
	$(PYTHON) -m pip install build -q
	$(PYTHON) -m build

check-dist: build-dist ## Validate distribution with twine
	$(PYTHON) -m pip install twine -q
	twine check dist/*

gameday-list: ## List available GameDay workflows
	python3 scripts/gameday.py --list

gameday: ## Run GameDay (make gameday GAMEDAY=quickstart)
	@if [ -z "$(GAMEDAY)" ]; then \
		echo "Usage: make gameday GAMEDAY=quickstart"; \
		python3 scripts/gameday.py --list; \
	else \
		python3 scripts/gameday.py $(GAMEDAY); \
	fi

slo-report: ## SLO report for an experiment (make slo-report EXPERIMENT=pod-delete)
	python3 scripts/quickstart_report.py --experiment $(or $(EXPERIMENT),pod-delete)
