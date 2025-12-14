#!/usr/bin/env python3
"""
Advanced Chaos Experiment Runner
Manages Phase 2 and Phase 3 chaos experiments with enhanced features
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from utils import (get_config, get_logger, run_command, validate_experiment_name, validate_namespace)

logger = get_logger(__name__)
config = get_config()


class AdvancedChaosRunner:
    def __init__(self):
        self.experiments_dir = Path(config.experiments_dir)
        self.namespace = config.app_namespace

    def list_phase_experiments(self):
        """List experiments by phase"""
        experiments = {
            "Phase 1 - Basic Infrastructure": ["pod-delete"],
            "Phase 2 - Basic Chaos Experiments": [
                "cpu-hog",
                "memory-hog",
                "network-latency",
            ],
            "Phase 3 - Advanced Chaos Experiments": [
                "network-partition",
                "disk-stress",
                "custom-chaos",
                "multi-cluster-chaos",
            ],
            "Advanced Workflows": ["chaos-workflow"],
        }

        logger.info("Available Chaos Experiments by Phase:")
        logger.info("=" * 50)

        for phase, exps in experiments.items():
            logger.info(f"\n{phase}:")
            for exp in exps:
                file_path = self.experiments_dir / f"{exp}.yaml"
                if file_path.exists():
                    logger.info(f"  ✅ {exp}")
                else:
                    logger.warning(f"  ❌ {exp} (missing)")

        return experiments

    def run_phase_experiment(self, phase_name, experiment_name):
        """Run a specific phase experiment"""
        # Validate experiment name
        try:
            experiment_name = validate_experiment_name(experiment_name)
        except ValueError as e:
            logger.error(f"Invalid experiment name: {e}")
            return

        logger.info(f"Running {phase_name}: {experiment_name}")

        # Check if experiment file exists
        experiment_file = self.experiments_dir / f"{experiment_name}.yaml"
        if not experiment_file.exists():
            logger.error(f"Experiment file not found: {experiment_file}")
            return

        # Apply the experiment
        result = run_command(f"kubectl apply -f {experiment_file}")
        if result:
            logger.info(f"✅ Applied experiment: {experiment_name}")
        else:
            logger.error(f"Failed to apply experiment: {experiment_name}")
            return

        # Wait for experiment to start
        logger.info("Waiting for experiment to start...")
        time.sleep(5)  # Brief wait before monitoring

        # Monitor the experiment
        self.monitor_experiment(experiment_name)

    def run_comprehensive_workflow(self):
        """Run the comprehensive chaos workflow"""
        logger.info("Running Comprehensive Chaos Workflow")
        logger.info("This will execute multiple experiments in sequence...")

        workflow_file = "chaos-workflow.yaml"
        workflow_path = self.experiments_dir / workflow_file
        if not workflow_path.exists():
            logger.error(f"Workflow file {workflow_path} not found")
            return

        # Apply the workflow
        result = run_command(f"kubectl apply -f {workflow_path}")
        if result:
            logger.info("✅ Applied comprehensive workflow")
        else:
            logger.error("Failed to apply comprehensive workflow")
            return

        # Monitor the workflow
        self.monitor_workflow()

    def monitor_experiment(self, experiment_name):
        """Monitor a running experiment"""
        logger.info(f"Monitoring experiment: {experiment_name}")

        # Check ChaosEngine status
        result = run_command(
            f"kubectl get chaosengine {experiment_name} -n {self.namespace} -o jsonpath='{{.status.engineStatus}}'",
            check=False,
        )
        if result:
            logger.info(f"Engine Status: {result}")
        else:
            logger.warning("Could not retrieve engine status")

        # Check for chaos pods
        result = run_command(
            f"kubectl get pods -n {self.namespace} -l job-name", check=False
        )
        if result:
            logger.info("Chaos Pods:")
            logger.info(result)

        # Check application pods
        result = run_command(f"kubectl get pods -n {self.namespace}", check=False)
        if result:
            logger.info("Application Pods:")
            logger.info(result)

    def monitor_workflow(self):
        """Monitor the comprehensive workflow"""
        logger.info("Monitoring comprehensive workflow...")

        # Check all chaos engines
        result = run_command(
            f"kubectl get chaosengine -n {self.namespace}", check=False
        )
        if result:
            logger.info("Active Chaos Engines:")
            logger.info(result)

        # Check application health
        result = run_command(
            f"kubectl get pods -n {self.namespace} -l app=flask-app", check=False
        )
        if result:
            logger.info("Application Pods Status:")
            logger.info(result)

    def run_phase_2_experiments(self):
        """Run all Phase 2 experiments"""
        logger.info("Running Phase 2: Basic Chaos Experiments")

        phase_2_experiments = ["pod-delete", "cpu-hog", "memory-hog", "network-latency"]

        for exp in phase_2_experiments:
            if (self.experiments_dir / f"{exp}.yaml").exists():
                logger.info(f"\n--- Running {exp} ---")
                self.run_phase_experiment("Phase 2", exp)
                time.sleep(10)  # Wait between experiments
            else:
                logger.warning(f"Experiment {exp} not found")

    def run_phase_3_experiments(self):
        """Run all Phase 3 experiments"""
        logger.info("Running Phase 3: Advanced Chaos Experiments")

        phase_3_experiments = ["network-partition", "disk-stress", "custom-chaos"]

        for exp in phase_3_experiments:
            if (self.experiments_dir / f"{exp}.yaml").exists():
                logger.info(f"\n--- Running {exp} ---")
                self.run_phase_experiment("Phase 3", exp)
                time.sleep(15)  # Wait between advanced experiments
            else:
                logger.warning(f"Experiment {exp} not found")

    def generate_experiment_report(self):
        """Generate a report of all experiments"""
        logger.info("Generating Chaos Experiment Report")

        report = {
            "timestamp": datetime.now().isoformat(),
            "namespace": self.namespace,
            "experiments": {},
        }

        # Get all chaos engines
        result = run_command(
            f"kubectl get chaosengine -n {self.namespace} -o json", check=False
        )
        if result:
            try:
                engines = json.loads(result)
                for engine in engines.get("items", []):
                    name = engine["metadata"]["name"]
                    status = engine.get("status", {})
                    report["experiments"][name] = {
                        "status": status.get("engineStatus", "Unknown"),
                        "experiments": status.get("experiments", []),
                    }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse chaos engines JSON: {e}")

        # Get application status
        result = run_command(
            f"kubectl get pods -n {self.namespace} -l app=flask-app -o json",
            check=False,
        )
        if result:
            try:
                pods = json.loads(result)
                report["application"] = {
                    "total_pods": len(pods.get("items", [])),
                    "ready_pods": len(
                        [
                            p
                            for p in pods.get("items", [])
                            if p["status"]["phase"] == "Running"
                        ]
                    ),
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse pods JSON: {e}")

        # Save report
        report_file = f"chaos_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"✅ Report saved to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None

        return report

    def cleanup_all_experiments(self):
        """Clean up all chaos experiments"""
        logger.info(
            f"Cleaning up all chaos experiments in namespace '{self.namespace}'..."
        )

        # Get all chaos engines
        result = run_command(
            f"kubectl get chaosengine -n {self.namespace} -o jsonpath='{{.items[*].metadata.name}}'",
            check=False,
        )
        if result:
            experiments = result.split()
            logger.info(f"Found {len(experiments)} experiment(s) to clean up")
            for exp in experiments:
                try:
                    validate_experiment_name(exp)
                    logger.info(f"Stopping experiment: {exp}")
                    run_command(
                        f'kubectl patch chaosengine {exp} -n {self.namespace} --type=\'merge\' -p \'{{"spec":{{"engineState":"stop"}}}}\'',
                        check=False,
                    )
                    run_command(
                        f"kubectl delete chaosengine {exp} -n {self.namespace}",
                        check=False,
                    )
                except ValueError as e:
                    logger.warning(f"Skipping invalid experiment name '{exp}': {e}")
        else:
            logger.info("No experiments to clean up")


def main():
    try:
        parser = argparse.ArgumentParser(description="Advanced Chaos Experiment Runner")
        parser.add_argument(
            "action",
            choices=[
                "list",
                "phase2",
                "phase3",
                "workflow",
                "report",
                "cleanup",
                "run",
            ],
            help="Action to perform",
        )
        parser.add_argument("--experiment", help="Specific experiment to run")

        args = parser.parse_args()

        runner = AdvancedChaosRunner()

        if args.action == "list":
            runner.list_phase_experiments()

        elif args.action == "phase2":
            runner.run_phase_2_experiments()

        elif args.action == "phase3":
            runner.run_phase_3_experiments()

        elif args.action == "workflow":
            runner.run_comprehensive_workflow()

        elif args.action == "report":
            runner.generate_experiment_report()

        elif args.action == "cleanup":
            runner.cleanup_all_experiments()

        elif args.action == "run":
            if not args.experiment:
                logger.error("Please specify an experiment with --experiment")
                sys.exit(1)
            runner.run_phase_experiment("Custom", args.experiment)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
