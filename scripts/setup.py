#!/usr/bin/env python3
"""
Kubernetes Chaos Engineering Setup Script
Automates the setup of the chaos engineering environment
"""

import sys
from pathlib import Path

from utils import (get_config, get_logger, run_command, wait_for_deployment,
                   wait_for_pods)

logger = get_logger(__name__)
config = get_config()


def check_prerequisites():
    """Check if required tools are installed"""
    logger.info("Checking prerequisites...")

    tools = ["kubectl", "helm"]
    for tool in tools:
        result = run_command(f"which {tool}", check=False)
        if not result:
            logger.error(f"{tool} is not installed. Please install it first.")
            return False
        logger.info(f"✅ {tool} found")

    # Check if kubectl can connect to cluster
    result = run_command("kubectl cluster-info", check=False)
    if not result:
        logger.error(
            "Cannot connect to Kubernetes cluster. Please ensure your cluster is running."
        )
        return False
    logger.info("✅ Connected to Kubernetes cluster")
    return True


def install_litmuschaos():
    """Install LitmusChaos using Helm"""
    logger.info("Installing LitmusChaos...")

    # Add LitmusChaos Helm repository
    run_command("helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/")
    run_command("helm repo update")

    # Install LitmusChaos
    run_command(
        f"helm install litmus litmuschaos/litmus --namespace {config.litmus_namespace} --create-namespace"
    )

    logger.info("Waiting for LitmusChaos pods to be ready...")
    try:
        wait_for_pods(
            namespace=config.litmus_namespace,
            timeout=config.default_timeout,
            check_interval=config.check_interval,
        )
        logger.info("✅ LitmusChaos pods are ready")
    except Exception as e:
        logger.error(f"Failed to wait for LitmusChaos pods: {e}")
        # Still show pod status
        result = run_command(
            f"kubectl get pods -n {config.litmus_namespace}", check=False
        )
        if result:
            logger.info(f"LitmusChaos pods status:\n{result}")
        raise


def deploy_sample_app():
    """Deploy the sample Flask application"""
    logger.info("Deploying sample Flask application...")

    # Apply the Flask app manifest
    manifest_path = Path(config.manifests_dir) / "flask-app.yaml"
    run_command(f"kubectl apply -f {manifest_path}")

    logger.info("Waiting for Flask app pods to be ready...")
    try:
        wait_for_pods(
            namespace=config.app_namespace,
            label_selector="app=flask-app",
            timeout=config.default_timeout,
            check_interval=config.check_interval,
        )
        logger.info("✅ Flask app pods are ready")
    except Exception as e:
        logger.error(f"Failed to wait for Flask app pods: {e}")
        # Still show pod status
        result = run_command(f"kubectl get pods -n {config.app_namespace}", check=False)
        if result:
            logger.info(f"Flask app pods status:\n{result}")
        raise


def setup_monitoring():
    """Setup Prometheus and Grafana monitoring"""
    if not config.monitoring_enabled:
        logger.info("Monitoring is disabled in configuration")
        return

    logger.info("Setting up monitoring...")

    # Add Prometheus Helm repository
    run_command(
        "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
    )
    run_command("helm repo update")

    # Install Prometheus stack
    run_command(
        f"helm install monitoring prometheus-community/kube-prometheus-stack --namespace {config.monitoring_namespace} --create-namespace"
    )

    logger.info("Waiting for monitoring pods to be ready...")
    try:
        wait_for_pods(
            namespace=config.monitoring_namespace,
            timeout=config.default_timeout,
            check_interval=config.check_interval,
        )
        logger.info("✅ Monitoring pods are ready")
    except Exception as e:
        logger.error(f"Failed to wait for monitoring pods: {e}")
        # Still show pod status
        result = run_command(
            f"kubectl get pods -n {config.monitoring_namespace}", check=False
        )
        if result:
            logger.info(f"Monitoring pods status:\n{result}")
        raise


def main():
    """Main setup function"""
    logger.info("Kubernetes Chaos Engineering Framework Setup")
    logger.info("=" * 50)

    if not check_prerequisites():
        sys.exit(1)

    # Ask user what to install
    print("\nWhat would you like to install?")
    print("1. LitmusChaos only")
    print("2. Sample application only")
    print("3. Monitoring only")
    print("4. Everything (recommended)")

    try:
        choice = input("Enter your choice (1-4): ").strip()

        if choice not in ["1", "2", "3", "4"]:
            logger.error("Invalid choice. Please enter 1, 2, 3, or 4.")
            sys.exit(1)

        if choice in ["1", "4"]:
            install_litmuschaos()

        if choice in ["2", "4"]:
            deploy_sample_app()

        if choice in ["3", "4"]:
            setup_monitoring()

        logger.info("✅ Setup completed!")
        print("\nNext steps:")
        print(
            f"1. Run chaos experiments: kubectl apply -f {config.experiments_dir}/pod-delete.yaml"
        )
        if config.monitoring_enabled:
            print(
                f"2. Access Grafana: kubectl port-forward svc/monitoring-grafana -n {config.monitoring_namespace} 3000:80"
            )
        print(
            f"3. Check application: kubectl port-forward svc/flask-app-service -n {config.app_namespace} 8080:80"
        )

    except KeyboardInterrupt:
        logger.info("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
