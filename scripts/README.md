# Automation Scripts

This directory contains Python automation scripts to simplify the setup and management of the Kubernetes Chaos Engineering Framework.

## Prerequisites

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Available Scripts

### setup.py

Automates the complete setup of the chaos engineering environment.

**Features:**
- Checks prerequisites (kubectl, helm, cluster connectivity)
- Installs LitmusChaos
- Deploys sample Flask application
- Sets up Prometheus and Grafana monitoring

**Usage:**
```bash
python scripts/setup.py
```

The script will prompt you to choose what to install:
1. LitmusChaos only
2. Sample application only
3. Monitoring only
4. Everything (recommended)

### chaos-runner.py

Manages chaos experiments with a simple command-line interface.

**Usage:**
```bash
# List available experiments
python scripts/chaos-runner.py list

# Run an experiment
python scripts/chaos-runner.py run <experiment-name>

# Check experiment status
python scripts/chaos-runner.py status <experiment-name>

# Stop an experiment
python scripts/chaos-runner.py stop <experiment-name>

# List running experiments
python scripts/chaos-runner.py running

# Clean up all experiments
python scripts/chaos-runner.py cleanup
```

**Available Experiments:**
- `pod-delete` - Deletes application pods to test resilience
- `cpu-hog` - Simulates CPU stress on application pods
- `disk-stress` - Simulates disk I/O stress
- `network-latency` - Introduces network latency

## Examples

### Quick Setup
```bash
# Complete setup
python scripts/setup.py

# Run a pod delete experiment
python scripts/chaos-runner.py run pod-delete

# Check the status
python scripts/chaos-runner.py status pod-delete

# Stop the experiment
python scripts/chaos-runner.py stop pod-delete
```

### Using Makefile
The project also includes a Makefile for convenience:

```bash
# Show all available commands
make help

# Run setup
make setup

# Run an experiment
make run-experiment EXPERIMENT=pod-delete

# Stop an experiment
make stop-experiment EXPERIMENT=pod-delete

# List experiments
make list-experiments
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure the scripts are executable:
   ```bash
   chmod +x scripts/*.py
   ```

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r scripts/requirements.txt
   ```

3. **Cluster Connection**: Ensure kubectl is configured:
   ```bash
   kubectl cluster-info
   ```

4. **Namespace Issues**: Make sure the hello-world-app namespace exists:
   ```bash
   kubectl apply -f manifests/namespace.yaml
   ```

### Logs and Debugging

- Check experiment logs: `kubectl logs -n hello-world-app -l job-name`
- Check application logs: `kubectl logs -n hello-world-app -l app=flask-app`
- Check LitmusChaos logs: `kubectl logs -n litmus -l app.kubernetes.io/name=litmus` 