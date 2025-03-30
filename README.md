# Kubernetes Chaos Engineering Demo

A complete chaos engineering implementation for Kubernetes featuring:
- Flask web application
- LitmusChaos experiments
- Prometheus monitoring
- Helm deployment

## Project Structure

```
k8s-chaos-engineering/
├── hello-world-app/          # Flask application
│   ├── app.py                # Flask web server
│   ├── Dockerfile            # Containerization
│   └── requirements.txt      # Python dependencies
│
├── deployments/              # Kubernetes resources
│   └── flask-app.yaml        # Deployment and service
│
├── experiments/              # Chaos experiments
│   ├── cpu-hog.yaml          # CPU stress test
│   ├── network-latency.yaml  # Network disruption
│   └── pod-delete.yaml       # Pod failure test
│
├── helm/                     # Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       └── service.yaml
│
└── monitoring/               # Observability
    └── prometheus.yaml       # Prometheus setup
```

## Prerequisites

- Kubernetes cluster
- Docker
- Helm v3+
- kubectl
- LitmusChaos operator

## Installation

1. **Build and push Docker image**:
```bash
docker build -t [YOUR_REGISTRY]/flask-chaos-demo:latest ./hello-world-app
docker push [YOUR_REGISTRY]/flask-chaos-demo:latest
```

2. **Deploy application**:
```bash
# Option 1: Direct deployment
kubectl apply -f deployments/

# Option 2: Helm deployment
helm install chaos-demo ./helm/
```

3. **Install monitoring**:
```bash
kubectl apply -f monitoring/
```

4. **Install LitmusChaos**:
```bash
kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v2.6.0.yaml
```

## Running Chaos Experiments

```bash
# Run all experiments
kubectl apply -f experiments/

# Or run individually
kubectl apply -f experiments/cpu-hog.yaml
kubectl apply -f experiments/network-latency.yaml
kubectl apply -f experiments/pod-delete.yaml
```

## Monitoring

Access Prometheus dashboard:
```bash
kubectl port-forward svc/prometheus 9090:9090
```
Then open http://localhost:9090

## Cleanup

```bash
# Remove chaos experiments
kubectl delete -f experiments/

# Uninstall application
kubectl delete -f deployments/
# OR if using Helm
helm uninstall chaos-demo

# Uninstall monitoring
kubectl delete -f monitoring/