.PHONY: help setup install-litmus deploy-app setup-monitoring run-experiment stop-experiment cleanup list-experiments phase2 phase3 workflow report

help: ## Show this help message
	@echo "Kubernetes Chaos Engineering Framework"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Run the automated setup script
	python scripts/setup.py

install-litmus: ## Install LitmusChaos
	helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
	helm repo update
	helm install litmus litmuschaos/litmus --namespace litmus --create-namespace

deploy-app: ## Deploy the sample Flask application
	kubectl apply -f manifests/flask-app.yaml

setup-monitoring: ## Setup Prometheus and Grafana monitoring
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

run-experiment: ## Run a chaos experiment (usage: make run-experiment EXPERIMENT=pod-delete)
	@if [ -z "$(EXPERIMENT)" ]; then \
		echo "Please specify an experiment: make run-experiment EXPERIMENT=<experiment-name>"; \
		echo "Available experiments:"; \
		python scripts/chaos-runner.py list; \
	else \
		python scripts/chaos-runner.py run $(EXPERIMENT); \
	fi

stop-experiment: ## Stop a chaos experiment (usage: make stop-experiment EXPERIMENT=pod-delete)
	@if [ -z "$(EXPERIMENT)" ]; then \
		echo "Please specify an experiment: make stop-experiment EXPERIMENT=<experiment-name>"; \
	else \
		python scripts/chaos-runner.py stop $(EXPERIMENT); \
	fi

cleanup: ## Clean up all chaos experiments
	python scripts/chaos-runner.py cleanup

list-experiments: ## List available chaos experiments
	python scripts/chaos-runner.py list

check-status: ## Check status of running experiments
	python scripts/chaos-runner.py running

port-forward-grafana: ## Port forward Grafana dashboard
	kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

port-forward-app: ## Port forward Flask application
	kubectl port-forward svc/flask-app-service -n hello-world-app 8080:80

phase2: ## Run all Phase 2 experiments
	python scripts/advanced-chaos-runner.py phase2

phase3: ## Run all Phase 3 experiments
	python scripts/advanced-chaos-runner.py phase3

workflow: ## Run comprehensive chaos workflow
	python scripts/advanced-chaos-runner.py workflow

report: ## Generate chaos experiment report
	python scripts/advanced-chaos-runner.py report

list-phases: ## List experiments by phase
	python scripts/advanced-chaos-runner.py list

setup-monitoring-advanced: ## Setup advanced monitoring with chaos dashboard
	kubectl apply -f monitoring/chaos-dashboard.yaml
	kubectl apply -f monitoring/chaos-alerts.yaml 