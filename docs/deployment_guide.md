# Deployment Guide

## Prerequisites

1. **Kubernetes Cluster Setup**
   ```bash
   # Verify cluster access
   kubectl cluster-info
   
   # Check node status
   kubectl get nodes
   ```

2. **Helm Installation**
   ```bash
   # Add required Helm repositories
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo add grafana https://grafana.github.io/helm-charts
   helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm
   
   # Update Helm repositories
   helm repo update
   ```

## Deployment Steps

### 1. Create Namespace
```bash
kubectl create namespace litmus
kubectl create namespace monitoring
```

### 2. Deploy MongoDB
```bash
# Create MongoDB secret
kubectl apply -f deployments/mongodb-secret.yaml

# Create MongoDB PVC
kubectl apply -f deployments/mongodb-pvc.yaml

# Deploy MongoDB
kubectl apply -f deployments/mongodb-deployment.yaml
```

### 3. Deploy Monitoring Stack
```bash
# Deploy Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f deployments/monitoring/prometheus-values.yaml

# Deploy Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  -f deployments/monitoring/grafana-values.yaml
```

### 4. Deploy LitmusChaos
```bash
# Deploy LitmusChaos
helm install litmus litmuschaos/litmus \
  --namespace litmus \
  -f deployments/litmus-values.yaml
```

### 5. Deploy Application
```bash
# Deploy Flask application
kubectl apply -f deployments/flask-app-deployment.yaml

# Deploy Nginx
kubectl apply -f deployments/nginx.yaml
```

## Verification

### 1. Check Pod Status
```bash
kubectl get pods -n litmus
kubectl get pods -n monitoring
kubectl get pods -n default
```

### 2. Verify Services
```bash
kubectl get svc -n litmus
kubectl get svc -n monitoring
kubectl get svc -n default
```

### 3. Access Applications
```bash
# Get Grafana admin password
kubectl get secret grafana-admin -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward services
kubectl port-forward svc/grafana 3000:80 -n monitoring
kubectl port-forward svc/litmus-portal 9091:9091 -n litmus
```

## Configuration

### 1. MongoDB Configuration
- Update connection string in `mongodb-secret.yaml`
- Adjust resource limits in `mongodb-deployment.yaml`
- Configure backup schedule

### 2. Monitoring Configuration
- Update Prometheus retention period
- Configure Grafana dashboards
- Set up alerting rules

### 3. Application Configuration
- Update environment variables
- Configure resource limits
- Set up logging

## Security Setup

### 1. Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: litmus
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 2. RBAC Configuration
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: litmus
  name: chaos-admin
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

### 3. Secret Management
- Use Kubernetes secrets
- Implement Vault integration
- Rotate credentials regularly

## Maintenance

### 1. Backup Procedures
```bash
# MongoDB backup
kubectl exec -it <mongodb-pod> -- mongodump --out=/backup

# Configuration backup
kubectl get all -n litmus -o yaml > litmus-backup.yaml
```

### 2. Update Procedures
```bash
# Update Helm releases
helm upgrade prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f deployments/monitoring/prometheus-values.yaml

# Update application
kubectl set image deployment/flask-app flask-app=flask-app:new-version
```

### 3. Monitoring Setup
- Configure Prometheus alerts
- Set up Grafana dashboards
- Implement logging aggregation

## Troubleshooting

### 1. Common Issues
- Pod startup failures
- Database connection issues
- Monitoring stack problems

### 2. Debug Procedures
```bash
# Check pod logs
kubectl logs <pod-name> -n <namespace>

# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check service endpoints
kubectl get endpoints <service-name> -n <namespace>
```

### 3. Recovery Procedures
- Database recovery
- Application rollback
- Configuration restoration

## Performance Tuning

### 1. Resource Optimization
- Adjust resource limits
- Configure horizontal pod autoscaling
- Optimize storage performance

### 2. Monitoring Optimization
- Fine-tune scrape intervals
- Optimize metric retention
- Configure efficient alerting

### 3. Application Tuning
- Optimize database queries
- Configure caching
- Implement connection pooling 