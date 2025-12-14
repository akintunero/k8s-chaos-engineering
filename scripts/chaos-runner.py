#!/usr/bin/env python3
"""
Chaos Experiment Runner
Manages and runs chaos experiments
"""

import sys
import time
from pathlib import Path

from utils import (ExperimentConfig, get_config, get_logger, run_command,
                   validate_experiment_name, validate_namespace)

logger = get_logger(__name__)
config = get_config()


def list_experiments():
    """List available chaos experiments"""
    experiments_dir = Path(config.experiments_dir)
    experiments = []

    if not experiments_dir.exists():
        logger.warning(f"Experiments directory not found: {experiments_dir}")
        return experiments

    for file in experiments_dir.glob("*.yaml"):
        if file.name != "rbac.yaml":
            experiments.append(file.stem)

    return experiments


def run_experiment(experiment_name: str, namespace: str = None):
    """Run a specific chaos experiment"""
    # Validate inputs
    try:
        experiment_name = validate_experiment_name(experiment_name)
        namespace = validate_namespace(namespace or config.app_namespace)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    logger.info(f"Running chaos experiment: {experiment_name}")

    # Check if experiment file exists
    experiment_file = Path(config.experiments_dir) / f"{experiment_name}.yaml"
    if not experiment_file.exists():
        logger.error(f"Experiment file not found: {experiment_file}")
        sys.exit(1)

    # Apply the experiment
    result = run_command(f"kubectl apply -f {experiment_file}")
    if result:
        logger.info(f"✅ Applied experiment: {experiment_name}")
    else:
        logger.error(f"Failed to apply experiment: {experiment_name}")
        sys.exit(1)

    # Wait for experiment to start
    logger.info("Waiting for experiment to start...")
    time.sleep(5)  # Brief wait before checking status

    # Check experiment status
    check_experiment_status(experiment_name, namespace)


def check_experiment_status(experiment_name: str, namespace: str = None):
    """Check the status of a running experiment"""
    namespace = namespace or config.app_namespace

    # Validate inputs
    try:
        experiment_name = validate_experiment_name(experiment_name)
        namespace = validate_namespace(namespace)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return

    logger.info(f"Checking status of experiment: {experiment_name}")

    # Check ChaosEngine status
    result = run_command(
        f"kubectl get chaosengine {experiment_name} -n {namespace} -o jsonpath='{{.status.engineStatus}}'",
        check=False,
    )
    if result:
        logger.info(f"Engine Status: {result}")
    else:
        logger.warning("Could not retrieve engine status")

    # Check for chaos pods
    result = run_command(f"kubectl get pods -n {namespace} -l job-name", check=False)
    if result:
        logger.info("Chaos Pods:")
        logger.info(result)

    # Check application pods
    result = run_command(f"kubectl get pods -n {namespace}", check=False)
    if result:
        logger.info("Application Pods:")
        logger.info(result)


def stop_experiment(experiment_name: str, namespace: str = None):
    """Stop a running chaos experiment"""
    namespace = namespace or config.app_namespace

    # Validate inputs
    try:
        experiment_name = validate_experiment_name(experiment_name)
        namespace = validate_namespace(namespace)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    logger.info(f"Stopping chaos experiment: {experiment_name}")

    # Stop the experiment
    result = run_command(
        f'kubectl patch chaosengine {experiment_name} -n {namespace} --type=\'merge\' -p \'{{"spec":{{"engineState":"stop"}}}}\'',
        check=False,
    )
    if not result:
        logger.warning(f"Failed to stop experiment: {experiment_name}")

    # Delete the experiment
    result = run_command(
        f"kubectl delete chaosengine {experiment_name} -n {namespace}", check=False
    )
    if result:
        logger.info(f"✅ Stopped and deleted experiment: {experiment_name}")
    else:
        logger.warning(f"Experiment may not exist: {experiment_name}")


def list_running_experiments(namespace: str = None):
    """List currently running chaos experiments"""
    namespace = namespace or config.app_namespace

    try:
        namespace = validate_namespace(namespace)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return

    logger.info(f"Currently running chaos experiments in namespace '{namespace}':")

    result = run_command(f"kubectl get chaosengine -n {namespace}", check=False)
    if result:
        logger.info(result)
    else:
        logger.info("No running experiments found")


def cleanup_experiments(namespace: str = None):
    """Clean up all chaos experiments"""
    namespace = namespace or config.app_namespace

    try:
        namespace = validate_namespace(namespace)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return

    logger.info(f"Cleaning up all chaos experiments in namespace '{namespace}'...")

    # Get all chaos engines
    result = run_command(
        f"kubectl get chaosengine -n {namespace} -o jsonpath='{{.items[*].metadata.name}}'",
        check=False,
    )
    if result:
        experiments = result.split()
        logger.info(f"Found {len(experiments)} experiment(s) to clean up")
        for exp in experiments:
            try:
                validate_experiment_name(exp)
                stop_experiment(exp, namespace)
            except ValueError as e:
                logger.warning(f"Skipping invalid experiment name '{exp}': {e}")
    else:
        logger.info("No experiments to clean up")


def main():
    """Main function"""
    logger.info("Chaos Experiment Runner")
    logger.info("=" * 30)

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python chaos-runner.py list                    # List available experiments"
        )
        print("  python chaos-runner.py run <experiment>        # Run an experiment")
        print(
            "  python chaos-runner.py status <experiment>     # Check experiment status"
        )
        print("  python chaos-runner.py stop <experiment>       # Stop an experiment")
        print(
            "  python chaos-runner.py running                 # List running experiments"
        )
        print(
            "  python chaos-runner.py cleanup                 # Clean up all experiments"
        )
        sys.exit(1)

    action = sys.argv[1]

    try:
        if action == "list":
            experiments = list_experiments()
            logger.info("Available experiments:")
            for exp in experiments:
                logger.info(f"  - {exp}")

        elif action == "run":
            if len(sys.argv) < 3:
                logger.error("Please specify an experiment to run")
                sys.exit(1)
            experiment = sys.argv[2]
            run_experiment(experiment)

        elif action == "status":
            if len(sys.argv) < 3:
                logger.error("Please specify an experiment to check")
                sys.exit(1)
            experiment = sys.argv[2]
            check_experiment_status(experiment)

        elif action == "stop":
            if len(sys.argv) < 3:
                logger.error("Please specify an experiment to stop")
                sys.exit(1)
            experiment = sys.argv[2]
            stop_experiment(experiment)

        elif action == "running":
            list_running_experiments()

        elif action == "cleanup":
            cleanup_experiments()

        else:
            logger.error(f"Unknown action: {action}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
