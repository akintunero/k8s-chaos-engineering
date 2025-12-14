#!/usr/bin/env python3
"""
Chaos Experiment Scheduler
Manages scheduled chaos experiments using Kubernetes CronJobs
"""

import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from utils import get_config, get_logger, run_command, validate_experiment_name, validate_namespace

logger = get_logger(__name__)
config = get_config()


class ChaosScheduler:
    """Manages scheduled chaos experiments"""

    def __init__(self):
        self.config = config
        self.namespace = config.app_namespace

    def create_scheduled_experiment(
        self,
        experiment_name: str,
        schedule: str,
        experiment_file: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """
        Create a scheduled chaos experiment using CronJob.

        Args:
            experiment_name: Name of the experiment
            schedule: Cron schedule (e.g., "0 2 * * *" for daily at 2 AM)
            experiment_file: Path to experiment YAML file
            namespace: Kubernetes namespace

        Returns:
            True if successful
        """
        namespace = namespace or self.namespace

        # Validate inputs
        try:
            experiment_name = validate_experiment_name(experiment_name)
            namespace = validate_namespace(namespace)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return False

        # Validate cron schedule format (basic check)
        if not self._validate_cron_schedule(schedule):
            logger.error(f"Invalid cron schedule: {schedule}")
            return False

        # Load experiment file
        if experiment_file:
            exp_path = Path(experiment_file)
        else:
            exp_path = Path(config.experiments_dir) / f"{experiment_name}.yaml"

        if not exp_path.exists():
            logger.error(f"Experiment file not found: {exp_path}")
            return False

        # Read experiment YAML
        try:
            with open(exp_path, "r") as f:
                experiment_yaml = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to read experiment file: {e}")
            return False

        # Create CronJob manifest
        cronjob = self._create_cronjob_manifest(
            experiment_name=experiment_name,
            schedule=schedule,
            experiment_yaml=experiment_yaml,
            namespace=namespace,
        )

        # Apply CronJob
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(cronjob, f)
            cronjob_file = Path(f.name)
        try:

            result = run_command(f"kubectl apply -f {cronjob_file}")
            if result:
                logger.info(f"✅ Created scheduled experiment: {experiment_name}")
                logger.info(f"   Schedule: {schedule}")
                logger.info(f"   Namespace: {namespace}")
                return True
            else:
                logger.error(
                    f"Failed to create scheduled experiment: {experiment_name}"
                )
                return False
        finally:
            if cronjob_file.exists():
                cronjob_file.unlink()

    def list_scheduled_experiments(self, namespace: Optional[str] = None) -> list:
        """List all scheduled chaos experiments"""
        namespace = namespace or self.namespace

        try:
            namespace = validate_namespace(namespace)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return []

        result = run_command(
            f"kubectl get cronjobs -n {namespace} -l app=chaos-scheduler -o json",
            check=False,
        )

        if not result:
            logger.info("No scheduled experiments found")
            return []

        import json

        try:
            cronjobs = json.loads(result)
            experiments = []
            for cj in cronjobs.get("items", []):
                experiments.append(
                    {
                        "name": cj["metadata"]["name"],
                        "schedule": cj["spec"]["schedule"],
                        "last_run": cj.get("status", {}).get("lastScheduleTime"),
                        "active": len(cj.get("status", {}).get("active", [])),
                    }
                )
            return experiments
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse CronJobs: {e}")
            return []

    def delete_scheduled_experiment(
        self, experiment_name: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete a scheduled experiment"""
        namespace = namespace or self.namespace

        try:
            experiment_name = validate_experiment_name(experiment_name)
            namespace = validate_namespace(namespace)
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return False

        cronjob_name = f"chaos-{experiment_name}"
        result = run_command(
            f"kubectl delete cronjob {cronjob_name} -n {namespace}", check=False
        )

        if result:
            logger.info(f"✅ Deleted scheduled experiment: {experiment_name}")
            return True
        else:
            logger.warning(f"Scheduled experiment not found: {experiment_name}")
            return False

    def _validate_cron_schedule(self, schedule: str) -> bool:
        """Basic validation of cron schedule format"""
        parts = schedule.split()
        if len(parts) != 5:
            return False

        # Basic format check (minute hour day month weekday)
        for part in parts:
            if not (
                part.isdigit()
                or part == "*"
                or "/" in part
                or "-" in part
                or "," in part
            ):
                return False

        return True

    def _create_cronjob_manifest(
        self,
        experiment_name: str,
        schedule: str,
        experiment_yaml: Dict[str, Any],
        namespace: str,
    ) -> Dict[str, Any]:
        """Create CronJob manifest for scheduled experiment"""

        cronjob_name = f"chaos-{experiment_name}"

        # Create a Job template that applies the experiment
        job_template = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{cronjob_name}-$(CRONJOB_SCHEDULE_TIME)",
                "namespace": namespace,
                "labels": {"app": "chaos-scheduler", "experiment": experiment_name},
            },
            "spec": {
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "chaos-scheduler",
                            "experiment": experiment_name,
                        }
                    },
                    "spec": {
                        "serviceAccountName": "litmus-admin",
                        "restartPolicy": "OnFailure",
                        "containers": [
                            {
                                "name": "chaos-runner",
                                "image": "bitnami/kubectl:latest",
                                "command": ["/bin/sh"],
                                "args": [
                                    "-c",
                                    f"kubectl apply -f - <<EOF\n{yaml.dump(experiment_yaml)}EOF",
                                ],
                            }
                        ],
                    },
                }
            },
        }

        cronjob = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": cronjob_name,
                "namespace": namespace,
                "labels": {"app": "chaos-scheduler", "experiment": experiment_name},
            },
            "spec": {
                "schedule": schedule,
                "jobTemplate": job_template["spec"],
                "successfulJobsHistoryLimit": 3,
                "failedJobsHistoryLimit": 3,
                "concurrencyPolicy": "Forbid",  # Don't run if previous job is still running
            },
        }

        return cronjob


def main():
    """CLI for chaos experiment scheduler"""
    import argparse

    parser = argparse.ArgumentParser(description="Chaos Experiment Scheduler")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create scheduled experiment
    create_parser = subparsers.add_parser(
        "create", help="Create a scheduled experiment"
    )
    create_parser.add_argument("experiment", help="Experiment name")
    create_parser.add_argument("schedule", help='Cron schedule (e.g., "0 2 * * *")')
    create_parser.add_argument("--file", help="Path to experiment YAML file")
    create_parser.add_argument("--namespace", help="Kubernetes namespace")

    # List scheduled experiments
    list_parser = subparsers.add_parser("list", help="List scheduled experiments")
    list_parser.add_argument("--namespace", help="Kubernetes namespace")

    # Delete scheduled experiment
    delete_parser = subparsers.add_parser(
        "delete", help="Delete a scheduled experiment"
    )
    delete_parser.add_argument("experiment", help="Experiment name")
    delete_parser.add_argument("--namespace", help="Kubernetes namespace")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    scheduler = ChaosScheduler()

    try:
        if args.command == "create":
            success = scheduler.create_scheduled_experiment(
                experiment_name=args.experiment,
                schedule=args.schedule,
                experiment_file=getattr(args, "file", None),
                namespace=getattr(args, "namespace", None),
            )
            sys.exit(0 if success else 1)

        elif args.command == "list":
            experiments = scheduler.list_scheduled_experiments(
                namespace=getattr(args, "namespace", None)
            )
            if experiments:
                logger.info("Scheduled experiments:")
                for exp in experiments:
                    logger.info(f"  - {exp['name']}: {exp['schedule']}")
            else:
                logger.info("No scheduled experiments found")

        elif args.command == "delete":
            success = scheduler.delete_scheduled_experiment(
                experiment_name=args.experiment,
                namespace=getattr(args, "namespace", None),
            )
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
