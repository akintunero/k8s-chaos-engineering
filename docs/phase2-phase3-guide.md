# Phase 2 & 3: Advanced Chaos Engineering Guide

## Overview

This guide covers the implementation of Phase 2 (Basic Chaos Experiments) and Phase 3 (Advanced Chaos Experiments) of the Kubernetes Chaos Engineering Framework.

## Phase 2: Basic Chaos Experiments

### Available Experiments

#### 1. Pod Delete Experiment
**Purpose**: Tests application resilience to pod failures
**File**: `experiments/pod-delete.yaml`

```bash
# Run pod delete experiment
python scripts/advanced-chaos-runner.py run --experiment pod-delete
```

**Parameters**:
- `TOTAL_CHAOS_DURATION`: Duration of the experiment (default: 30s)
- `CHAOS_INTERVAL`: Interval between chaos injections (default: 10s)
- `FORCE`: Force pod deletion (default: false)

#### 2. CPU Stress Experiment
**Purpose**: Simulates high CPU load scenarios
**File**: `experiments/cpu-hog.yaml`

```bash
# Run CPU stress experiment
python scripts/advanced-chaos-runner.py run --experiment cpu-hog
```

**Parameters**:
- `CPU_CORES`: Number of CPU cores to stress (default: 2)
- `CPU_LOAD`: Percentage of CPU to consume (default: 90%)
- `NUMBER_OF_WORKERS`: Number of worker processes (default: 4)

#### 3. Memory Stress Experiment
**Purpose**: Tests memory pressure handling
**File**: `experiments/memory-hog.yaml`

```bash
# Run memory stress experiment
python scripts/advanced-chaos-runner.py run --experiment memory-hog
```

**Parameters**:
- `MEMORY_CONSUMPTION`: Memory to consume in MB (default: 500MB)
- `NUMBER_OF_WORKERS`: Number of worker processes (default: 4)

#### 4. Network Latency Experiment
**Purpose**: Introduces network delays
**File**: `experiments/network-latency.yaml`

```bash
# Run network latency experiment
python scripts/advanced-chaos-runner.py run --experiment network-latency
```

**Parameters**:
- `NETWORK_LATENCY`: Latency in milliseconds (default: 2000ms)
- `NETWORK_JITTER`: Jitter in milliseconds (default: 100ms)
- `PACKET_LOSS_PERCENTAGE`: Packet loss percentage (default: 5%)

## Phase 3: Advanced Chaos Experiments

### Available Experiments

#### 1. Network Partition Experiment
**Purpose**: Simulates network isolation scenarios
**File**: `experiments/network-partition.yaml`

```bash
# Run network partition experiment
python scripts/advanced-chaos-runner.py run --experiment network-partition
```

**Parameters**:
- `NETWORK_PARTITION_MODE`: Mode of partition (loss, delay, duplicate, corrupt)
- `PACKET_LOSS_PERCENTAGE`: Percentage of packets to drop (default: 100%)

#### 2. Disk I/O Stress Experiment
**Purpose**: Tests storage performance under load
**File**: `experiments/disk-stress.yaml`

```bash
# Run disk stress experiment
python scripts/advanced-chaos-runner.py run --experiment disk-stress
```

**Parameters**:
- `DISK_FILL_PERCENTAGE`: Percentage of disk to fill (default: 80%)
- `DISK_IO_OPERATIONS`: IOPS to generate (default: 1000)
- `DISK_IO_PATTERN`: I/O pattern (random, sequential)

#### 3. Custom Chaos Experiment
**Purpose**: Multi-experiment orchestration
**File**: `experiments/custom-chaos.yaml`

```bash
# Run custom chaos experiment
python scripts/advanced-chaos-runner.py run --experiment custom-chaos
```

This experiment combines multiple chaos types:
- Pod deletion
- CPU stress
- Memory stress

#### 4. Multi-cluster Chaos Experiment
**Purpose**: Cross-cluster failure testing
**File**: `experiments/multi-cluster-chaos.yaml`

```bash
# Run multi-cluster chaos experiment
python scripts/advanced-chaos-runner.py run --experiment multi-cluster-chaos
```

**Parameters**:
- `TARGET_CLUSTER`: Target cluster (primary, secondary, all)
- `CLUSTER_SELECTOR`: Cluster selector labels

## Comprehensive Chaos Workflow

### Overview
The comprehensive workflow (`experiments/chaos-workflow.yaml`) orchestrates multiple experiments in sequence to test application resilience comprehensively.

### Workflow Phases

1. **Phase 1: Basic Infrastructure Chaos**
   - Pod deletion to test recovery

2. **Phase 2: Resource Stress**
   - CPU stress followed by memory stress

3. **Phase 3: Network Chaos**
   - Network latency introduction

4. **Phase 4: Storage Chaos**
   - Disk I/O stress testing

### Running the Workflow

```bash
# Run comprehensive workflow
python scripts/advanced-chaos-runner.py workflow

# Or using Makefile
make workflow
```

## Advanced Monitoring

### Chaos Dashboard
A custom Grafana dashboard (`monitoring/chaos-dashboard.yaml`) provides:
- Application pod status
- CPU usage during chaos
- Memory usage during chaos
- Network latency metrics
- Chaos experiment status

### Alerting Rules
Prometheus alerting rules (`monitoring/chaos-alerts.yaml`) include:
- Chaos experiment failure alerts
- Application pod down alerts
- High resource usage alerts
- Network latency alerts
- Disk space alerts

### Setup Advanced Monitoring

```bash
# Setup advanced monitoring
make setup-monitoring-advanced

# Or manually
kubectl apply -f monitoring/chaos-dashboard.yaml
kubectl apply -f monitoring/chaos-alerts.yaml
```

## Experiment Management

### Running Experiments by Phase

```bash
# Run all Phase 2 experiments
python scripts/advanced-chaos-runner.py phase2

# Run all Phase 3 experiments
python scripts/advanced-chaos-runner.py phase3

# List experiments by phase
python scripts/advanced-chaos-runner.py list
```

### Monitoring Experiments

```bash
# Generate experiment report
python scripts/advanced-chaos-runner.py report

# Check experiment status
kubectl get chaosengine -n hello-world-app

# View experiment logs
kubectl logs -n hello-world-app -l job-name
```

### Cleanup

```bash
# Clean up all experiments
python scripts/advanced-chaos-runner.py cleanup

# Or using Makefile
make cleanup
```

## Best Practices

### 1. Experiment Planning
- Start with Phase 2 experiments before moving to Phase 3
- Run experiments during low-traffic periods
- Have monitoring in place before running experiments

### 2. Safety Measures
- Always have a rollback plan
- Monitor application health during experiments
- Set appropriate timeouts and intervals

### 3. Documentation
- Document experiment results
- Track application behavior changes
- Maintain experiment history

### 4. Team Coordination
- Notify team members before running experiments
- Have incident response procedures ready
- Coordinate with monitoring teams

## Troubleshooting

### Common Issues

1. **Experiments not starting**
   - Check RBAC permissions
   - Verify namespace exists
   - Check LitmusChaos installation

2. **Application not recovering**
   - Check application health checks
   - Verify resource limits
   - Review application logs

3. **Monitoring not working**
   - Check Prometheus/Grafana installation
   - Verify service discovery
   - Check alert manager configuration

### Debug Commands

```bash
# Check experiment status
kubectl describe chaosengine <experiment-name> -n hello-world-app

# View chaos pod logs
kubectl logs -n hello-world-app -l job-name

# Check application logs
kubectl logs -n hello-world-app -l app=flask-app

# Verify RBAC
kubectl get serviceaccount litmus-admin -n hello-world-app
```

## Next Steps

With Phase 2 and Phase 3 implemented, consider:

1. **Phase 4**: Enhanced monitoring and analytics
2. **Phase 5**: Integration with CI/CD pipelines
3. **Phase 6**: Multi-cloud chaos experiments
4. **Custom Experiments**: Develop application-specific chaos tests

For more information, refer to the main [README.md](../Readme.md) and [ROADMAP.md](../ROADMAP.md). 