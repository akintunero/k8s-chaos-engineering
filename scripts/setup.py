#!/usr/bin/env python3
"""
Kubernetes Chaos Engineering Setup Script
Automates the setup of the chaos engineering environment
"""

import subprocess
import sys
import time
import yaml
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

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    tools = ['kubectl', 'helm']
    for tool in tools:
        result = run_command(f"which {tool}", check=False)
        if not result:
            print(f"❌ {tool} is not installed. Please install it first.")
            return False
        print(f"✅ {tool} found")
    
    # Check if kubectl can connect to cluster
    result = run_command("kubectl cluster-info", check=False)
    if not result:
        print("❌ Cannot connect to Kubernetes cluster. Please ensure your cluster is running.")
        return False
    print("✅ Connected to Kubernetes cluster")
    return True

def install_litmuschaos():
    """Install LitmusChaos using Helm"""
    print("🚀 Installing LitmusChaos...")
    
    # Add LitmusChaos Helm repository
    run_command("helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/")
    run_command("helm repo update")
    
    # Install LitmusChaos
    run_command("helm install litmus litmuschaos/litmus --namespace litmus --create-namespace")
    
    print("⏳ Waiting for LitmusChaos pods to be ready...")
    time.sleep(30)
    
    # Check pod status
    result = run_command("kubectl get pods -n litmus")
    print("📊 LitmusChaos pods status:")
    print(result)

def deploy_sample_app():
    """Deploy the sample Flask application"""
    print("📦 Deploying sample Flask application...")
    
    # Apply the Flask app manifest
    run_command("kubectl apply -f manifests/flask-app.yaml")
    
    print("⏳ Waiting for Flask app pods to be ready...")
    time.sleep(20)
    
    # Check pod status
    result = run_command("kubectl get pods -n hello-world-app")
    print("📊 Flask app pods status:")
    print(result)

def setup_monitoring():
    """Setup Prometheus and Grafana monitoring"""
    print("📊 Setting up monitoring...")
    
    # Add Prometheus Helm repository
    run_command("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run_command("helm repo update")
    
    # Install Prometheus stack
    run_command("helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace")
    
    print("⏳ Waiting for monitoring pods to be ready...")
    time.sleep(30)
    
    # Check pod status
    result = run_command("kubectl get pods -n monitoring")
    print("📊 Monitoring pods status:")
    print(result)

def main():
    """Main setup function"""
    print("🎯 Kubernetes Chaos Engineering Framework Setup")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    # Ask user what to install
    print("\nWhat would you like to install?")
    print("1. LitmusChaos only")
    print("2. Sample application only")
    print("3. Monitoring only")
    print("4. Everything (recommended)")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice in ['1', '4']:
        install_litmuschaos()
    
    if choice in ['2', '4']:
        deploy_sample_app()
    
    if choice in ['3', '4']:
        setup_monitoring()
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Run chaos experiments: kubectl apply -f experiments/pod-delete.yaml")
    print("2. Access Grafana: kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80")
    print("3. Check application: kubectl port-forward svc/flask-app-service -n hello-world-app 8080:80")

if __name__ == "__main__":
    main() 