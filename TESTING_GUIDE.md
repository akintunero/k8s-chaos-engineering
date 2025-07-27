# 🧪 Testing Guide for Chaos Engineering Framework

## Prerequisites Setup

### 1. Start Docker Desktop
1. Open Docker Desktop application
2. Go to Settings → Kubernetes
3. Enable Kubernetes
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (this may take a few minutes)

### 2. Verify Setup
```bash
# Run the setup verification script
./scripts/setup-cluster.sh
```

## 🚀 Quick Start Testing

### Step 1: Automated Setup
```bash
# Run the automated setup script
python scripts/setup.py
```
Choose option 4 (Everything) when prompted.

### Step 2: Verify Installation
```bash
# Check if everything is running
kubectl get pods -n litmus
kubectl get pods -n hello-world-app
kubectl get pods -n monitoring
```

### Step 3: List Available Experiments
```bash
# List all experiments by phase
python scripts/advanced-chaos-runner.py list
```

## 🎯 Testing Phase 2 Experiments

### Test 1: Pod Delete Experiment
```bash
# Run pod delete experiment
python scripts/advanced-chaos-runner.py run --experiment pod-delete

# Monitor the experiment
kubectl get pods -n hello-world-app
kubectl get chaosengine -n hello-world-app

# Check experiment logs
kubectl logs -n hello-world-app -l job-name
```

### Test 2: CPU Stress Experiment
```bash
# Run CPU stress experiment
python scripts/advanced-chaos-runner.py run --experiment cpu-hog

# Monitor CPU usage
kubectl top pods -n hello-world-app
```

### Test 3: Memory Stress Experiment
```bash
# Run memory stress experiment
python scripts/advanced-chaos-runner.py run --experiment memory-hog

# Monitor memory usage
kubectl top pods -n hello-world-app
```

### Test 4: Network Latency Experiment
```bash
# Run network latency experiment
python scripts/advanced-chaos-runner.py run --experiment network-latency

# Test network connectivity
kubectl exec -n hello-world-app deployment/flask-app -- curl -w "%{time_total}" -o /dev/null -s http://localhost:8080/health
```

## 🚀 Testing Phase 3 Experiments

### Test 1: Network Partition Experiment
```bash
# Run network partition experiment
python scripts/advanced-chaos-runner.py run --experiment network-partition

# Monitor network connectivity
kubectl exec -n hello-world-app deployment/flask-app -- ping -c 3 google.com
```

### Test 2: Disk Stress Experiment
```bash
# Run disk stress experiment
python scripts/advanced-chaos-runner.py run --experiment disk-stress

# Monitor disk usage
kubectl exec -n hello-world-app deployment/flask-app -- df -h
```

### Test 3: Custom Chaos Experiment
```bash
# Run custom chaos experiment (combines multiple experiments)
python scripts/advanced-chaos-runner.py run --experiment custom-chaos

# Monitor all aspects
kubectl get chaosengine -n hello-world-app
kubectl get pods -n hello-world-app
```

## 🔄 Testing Comprehensive Workflow

### Run Complete Workflow
```bash
# Run the comprehensive chaos workflow
python scripts/advanced-chaos-runner.py workflow

# Or using Makefile
make workflow
```

This will execute:
1. Pod deletion
2. CPU stress
3. Memory stress
4. Network latency
5. Disk stress

### Monitor Workflow Progress
```bash
# Check all chaos engines
kubectl get chaosengine -n hello-world-app

# Check application health
kubectl get pods -n hello-world-app

# Check experiment logs
kubectl logs -n hello-world-app -l job-name
```

## 📊 Testing Monitoring and Reporting

### Access Grafana Dashboard
```bash
# Port forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Open http://localhost:3000 in your browser
# Login: admin/admin
```

### Generate Experiment Report
```bash
# Generate a comprehensive report
python scripts/advanced-chaos-runner.py report

# Check the generated report
ls -la chaos_report_*.json
```

### Test Alerts
```bash
# Check if alerts are configured
kubectl get prometheusrule -n monitoring

# View alert manager
kubectl port-forward svc/monitoring-kube-prometheus-alertmanager -n monitoring 9093:9093
```

## 🧹 Cleanup and Reset

### Stop All Experiments
```bash
# Clean up all running experiments
python scripts/advanced-chaos-runner.py cleanup

# Or using Makefile
make cleanup
```

### Reset Application
```bash
# Delete and recreate the application
kubectl delete -f manifests/flask-app.yaml
kubectl apply -f manifests/flask-app.yaml
```

### Complete Reset
```bash
# Delete all namespaces and start fresh
kubectl delete namespace hello-world-app
kubectl delete namespace litmus
kubectl delete namespace monitoring

# Re-run setup
python scripts/setup.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Experiments not starting**
   ```bash
   # Check RBAC
   kubectl get serviceaccount litmus-admin -n hello-world-app
   
   # Check namespace
   kubectl get namespace hello-world-app
   
   # Check LitmusChaos installation
   kubectl get pods -n litmus
   ```

2. **Application not responding**
   ```bash
   # Check application logs
   kubectl logs -n hello-world-app -l app=flask-app
   
   # Check application health
   kubectl get pods -n hello-world-app
   
   # Test application directly
   kubectl port-forward svc/flask-app-service -n hello-world-app 8080:80
   curl http://localhost:8080/health
   ```

3. **Monitoring not working**
   ```bash
   # Check Prometheus
   kubectl get pods -n monitoring
   
   # Check Grafana
   kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
   
   # Check service discovery
   kubectl get endpoints -n monitoring
   ```

### Debug Commands

```bash
# Get detailed experiment information
kubectl describe chaosengine <experiment-name> -n hello-world-app

# View chaos pod logs
kubectl logs -n hello-world-app -l job-name

# Check resource usage
kubectl top pods -n hello-world-app

# Check events
kubectl get events -n hello-world-app --sort-by='.lastTimestamp'
```

## 📈 Expected Results

### Phase 2 Experiments
- **Pod Delete**: Application pods should be deleted and recreated automatically
- **CPU Stress**: CPU usage should spike to 80-90%
- **Memory Stress**: Memory usage should increase significantly
- **Network Latency**: Response times should increase by 2+ seconds

### Phase 3 Experiments
- **Network Partition**: Network connectivity should be disrupted
- **Disk Stress**: Disk I/O should be stressed
- **Custom Chaos**: Multiple effects should be observed simultaneously
- **Workflow**: Sequential execution of multiple experiments

### Monitoring
- Grafana dashboard should show real-time metrics
- Alerts should trigger based on thresholds
- Reports should contain detailed experiment data

## 🎉 Success Criteria

✅ All experiments execute without errors  
✅ Application recovers from failures  
✅ Monitoring captures metrics correctly  
✅ Alerts trigger appropriately  
✅ Reports are generated successfully  
✅ Cleanup works properly  

## 🚀 Next Steps

After successful testing:
1. Customize experiment parameters for your environment
2. Create application-specific chaos tests
3. Integrate with CI/CD pipelines
4. Set up production monitoring
5. Train team on chaos engineering practices

Happy testing! 🎯 