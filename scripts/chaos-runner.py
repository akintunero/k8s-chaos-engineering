#!/usr/bin/env python3
"""
Chaos Experiment Runner
Manages and runs chaos experiments
"""

import subprocess
import sys
import time
import yaml
import json
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def list_experiments():
    """List available chaos experiments"""
    experiments_dir = Path("experiments")
    experiments = []
    
    for file in experiments_dir.glob("*.yaml"):
        if file.name != "rbac.yaml":
            experiments.append(file.stem)
    
    return experiments

def run_experiment(experiment_name):
    """Run a specific chaos experiment"""
    print(f"🚀 Running chaos experiment: {experiment_name}")
    
    # Apply the experiment
    result = run_command(f"kubectl apply -f experiments/{experiment_name}.yaml")
    print(f"✅ Applied experiment: {experiment_name}")
    
    # Wait for experiment to start
    print("⏳ Waiting for experiment to start...")
    time.sleep(10)
    
    # Check experiment status
    check_experiment_status(experiment_name)

def check_experiment_status(experiment_name):
    """Check the status of a running experiment"""
    print(f"📊 Checking status of experiment: {experiment_name}")
    
    # Check ChaosEngine status
    result = run_command(f"kubectl get chaosengine {experiment_name} -n hello-world-app -o jsonpath='{{.status.engineStatus}}'", check=False)
    if result:
        print(f"Engine Status: {result}")
    
    # Check for chaos pods
    result = run_command("kubectl get pods -n hello-world-app -l job-name", check=False)
    if result:
        print("Chaos Pods:")
        print(result)
    
    # Check application pods
    result = run_command("kubectl get pods -n hello-world-app", check=False)
    if result:
        print("Application Pods:")
        print(result)

def stop_experiment(experiment_name):
    """Stop a running chaos experiment"""
    print(f"🛑 Stopping chaos experiment: {experiment_name}")
    
    # Stop the experiment
    run_command(f"kubectl patch chaosengine {experiment_name} -n hello-world-app --type='merge' -p '{{\"spec\":{{\"engineState\":\"stop\"}}}}'")
    
    # Delete the experiment
    run_command(f"kubectl delete chaosengine {experiment_name} -n hello-world-app")
    
    print(f"✅ Stopped and deleted experiment: {experiment_name}")

def list_running_experiments():
    """List currently running chaos experiments"""
    print("📋 Currently running chaos experiments:")
    
    result = run_command("kubectl get chaosengine -n hello-world-app", check=False)
    if result:
        print(result)
    else:
        print("No running experiments found")

def cleanup_experiments():
    """Clean up all chaos experiments"""
    print("🧹 Cleaning up all chaos experiments...")
    
    # Get all chaos engines
    result = run_command("kubectl get chaosengine -n hello-world-app -o jsonpath='{.items[*].metadata.name}'", check=False)
    if result:
        experiments = result.split()
        for exp in experiments:
            stop_experiment(exp)
    else:
        print("No experiments to clean up")

def main():
    """Main function"""
    print("🎯 Chaos Experiment Runner")
    print("=" * 30)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python chaos-runner.py list                    # List available experiments")
        print("  python chaos-runner.py run <experiment>        # Run an experiment")
        print("  python chaos-runner.py status <experiment>     # Check experiment status")
        print("  python chaos-runner.py stop <experiment>       # Stop an experiment")
        print("  python chaos-runner.py running                 # List running experiments")
        print("  python chaos-runner.py cleanup                 # Clean up all experiments")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "list":
        experiments = list_experiments()
        print("Available experiments:")
        for exp in experiments:
            print(f"  - {exp}")
    
    elif action == "run":
        if len(sys.argv) < 3:
            print("Please specify an experiment to run")
            sys.exit(1)
        experiment = sys.argv[2]
        run_experiment(experiment)
    
    elif action == "status":
        if len(sys.argv) < 3:
            print("Please specify an experiment to check")
            sys.exit(1)
        experiment = sys.argv[2]
        check_experiment_status(experiment)
    
    elif action == "stop":
        if len(sys.argv) < 3:
            print("Please specify an experiment to stop")
            sys.exit(1)
        experiment = sys.argv[2]
        stop_experiment(experiment)
    
    elif action == "running":
        list_running_experiments()
    
    elif action == "cleanup":
        cleanup_experiments()
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main() 