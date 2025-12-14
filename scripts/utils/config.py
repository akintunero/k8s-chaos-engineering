"""
Configuration management system
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class Config:
    """Centralized configuration for chaos engineering framework"""

    # Namespaces
    app_namespace: str = "hello-world-app"
    litmus_namespace: str = "litmus"
    monitoring_namespace: str = "monitoring"

    # Chaos settings
    default_timeout: int = 300
    retry_attempts: int = 3
    retry_delay: int = 1
    check_interval: int = 5

    # Monitoring
    monitoring_enabled: bool = True
    prometheus_url: str = "http://prometheus:9090"
    grafana_url: str = "http://grafana:3000"

    # Experiment defaults
    default_experiment_duration: int = 60
    default_chaos_interval: int = 10

    # Paths
    experiments_dir: str = "experiments"
    manifests_dir: str = "manifests"

    # Kubernetes
    kubeconfig: Optional[str] = None

    # Notifications
    notifications_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    email_enabled: bool = False
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_from: Optional[str] = None
    email_to: Optional[str] = None

    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "Config":
        """
        Load configuration from YAML file with environment variable overrides.

        Args:
            config_path: Path to config file (default: config/config.yaml)

        Returns:
            Config instance
        """
        if config_path is None:
            # Try to find config file
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "config.yaml"

        config_path = Path(config_path)

        # Load from file if exists
        file_config: Dict[str, Any] = {}
        if config_path.exists():
            logger.info(f"Loading configuration from {config_path}")
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config file not found at {config_path}, using defaults")

        # Flatten nested config structure
        config_dict: Dict[str, Any] = {}

        # Extract namespaces
        if "namespaces" in file_config:
            config_dict["app_namespace"] = file_config["namespaces"].get(
                "app", "hello-world-app"
            )
            config_dict["litmus_namespace"] = file_config["namespaces"].get(
                "litmus", "litmus"
            )
            config_dict["monitoring_namespace"] = file_config["namespaces"].get(
                "monitoring", "monitoring"
            )

        # Extract chaos settings
        if "chaos" in file_config:
            chaos = file_config["chaos"]
            config_dict["default_timeout"] = chaos.get("default_timeout", 300)
            config_dict["retry_attempts"] = chaos.get("retry_attempts", 3)
            config_dict["retry_delay"] = chaos.get("retry_delay", 1)
            config_dict["check_interval"] = chaos.get("check_interval", 5)
            config_dict["default_experiment_duration"] = chaos.get(
                "default_experiment_duration", 60
            )
            config_dict["default_chaos_interval"] = chaos.get(
                "default_chaos_interval", 10
            )

        # Extract monitoring
        if "monitoring" in file_config:
            monitoring = file_config["monitoring"]
            config_dict["monitoring_enabled"] = monitoring.get("enabled", True)
            config_dict["prometheus_url"] = monitoring.get(
                "prometheus_url", "http://prometheus:9090"
            )
            config_dict["grafana_url"] = monitoring.get(
                "grafana_url", "http://grafana:3000"
            )

        # Extract paths
        if "paths" in file_config:
            paths = file_config["paths"]
            config_dict["experiments_dir"] = paths.get("experiments_dir", "experiments")
            config_dict["manifests_dir"] = paths.get("manifests_dir", "manifests")

        # Extract kubernetes
        if "kubernetes" in file_config:
            config_dict["kubeconfig"] = file_config["kubernetes"].get("kubeconfig")

        # Extract notifications
        if "notifications" in file_config:
            notifications = file_config["notifications"]
            config_dict["notifications_enabled"] = notifications.get("enabled", False)
            if "slack" in notifications:
                config_dict["slack_webhook_url"] = notifications["slack"].get(
                    "webhook_url"
                )
            if "email" in notifications:
                email = notifications["email"]
                config_dict["email_enabled"] = email.get("enabled", False)
                config_dict["email_smtp_server"] = email.get("smtp_server")
                config_dict["email_smtp_port"] = email.get("smtp_port", 587)
                config_dict["email_from"] = email.get("from")
                config_dict["email_to"] = email.get("to")

        # Override with environment variables
        env_mappings = {
            "APP_NAMESPACE": "app_namespace",
            "LITMUS_NAMESPACE": "litmus_namespace",
            "MONITORING_NAMESPACE": "monitoring_namespace",
            "DEFAULT_TIMEOUT": "default_timeout",
            "RETRY_ATTEMPTS": "retry_attempts",
            "RETRY_DELAY": "retry_delay",
            "CHECK_INTERVAL": "check_interval",
            "MONITORING_ENABLED": "monitoring_enabled",
            "PROMETHEUS_URL": "prometheus_url",
            "GRAFANA_URL": "grafana_url",
            "EXPERIMENTS_DIR": "experiments_dir",
            "MANIFESTS_DIR": "manifests_dir",
            "KUBECONFIG": "kubeconfig",
            "NOTIFICATIONS_ENABLED": "notifications_enabled",
            "SLACK_WEBHOOK_URL": "slack_webhook_url",
            "EMAIL_ENABLED": "email_enabled",
            "EMAIL_SMTP_SERVER": "email_smtp_server",
            "EMAIL_SMTP_PORT": "email_smtp_port",
            "EMAIL_FROM": "email_from",
            "EMAIL_TO": "email_to",
        }

        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string to appropriate type
                if config_key in [
                    "default_timeout",
                    "retry_attempts",
                    "retry_delay",
                    "check_interval",
                    "default_experiment_duration",
                    "default_chaos_interval",
                    "email_smtp_port",
                ]:
                    config_dict[config_key] = int(env_value)
                elif config_key in [
                    "monitoring_enabled",
                    "notifications_enabled",
                    "email_enabled",
                ]:
                    config_dict[config_key] = env_value.lower() in (
                        "true",
                        "1",
                        "yes",
                        "on",
                    )
                else:
                    config_dict[config_key] = env_value
                logger.debug(f"Overriding {config_key} from environment: {env_value}")

        # Create config instance, using defaults for missing values
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "app_namespace": self.app_namespace,
            "litmus_namespace": self.litmus_namespace,
            "monitoring_namespace": self.monitoring_namespace,
            "default_timeout": self.default_timeout,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "check_interval": self.check_interval,
            "monitoring_enabled": self.monitoring_enabled,
            "prometheus_url": self.prometheus_url,
            "grafana_url": self.grafana_url,
            "default_experiment_duration": self.default_experiment_duration,
            "default_chaos_interval": self.default_chaos_interval,
            "experiments_dir": self.experiments_dir,
            "manifests_dir": self.manifests_dir,
            "kubeconfig": self.kubeconfig,
            "notifications_enabled": self.notifications_enabled,
            "slack_webhook_url": self.slack_webhook_url,
            "email_enabled": self.email_enabled,
            "email_smtp_server": self.email_smtp_server,
            "email_smtp_port": self.email_smtp_port,
            "email_from": self.email_from,
            "email_to": self.email_to,
        }


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file and environment variables.

    Args:
        config_path: Path to config file

    Returns:
        Config instance
    """
    return Config.from_file(config_path)


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance (singleton)"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
