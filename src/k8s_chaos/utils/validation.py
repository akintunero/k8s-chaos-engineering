"""
Input validation and sanitization
"""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .logging import get_logger

logger = get_logger(__name__)


# Kubernetes resource name validation regex
# Must be lowercase alphanumeric characters or '-', start and end with alphanumeric
K8S_NAME_REGEX = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
K8S_NAME_MAX_LENGTH = 253


def validate_experiment_name(name: str) -> str:
    """
    Validate and sanitize experiment name.

    Args:
        name: Experiment name to validate

    Returns:
        Validated experiment name

    Raises:
        ValueError: If name is invalid
    """
    if not name:
        raise ValueError("Experiment name cannot be empty")

    # Remove any whitespace
    name = name.strip()

    # Check length
    if len(name) > K8S_NAME_MAX_LENGTH:
        raise ValueError(
            f"Experiment name too long (max {K8S_NAME_MAX_LENGTH} characters)"
        )

    # Check format
    if not K8S_NAME_REGEX.match(name):
        raise ValueError(
            "Experiment name must be lowercase alphanumeric characters or '-', "
            "and must start and end with alphanumeric character"
        )

    return name


def validate_namespace(namespace: str) -> str:
    """
    Validate and sanitize namespace name.

    Args:
        namespace: Namespace name to validate

    Returns:
        Validated namespace name

    Raises:
        ValueError: If namespace is invalid
    """
    if not namespace:
        raise ValueError("Namespace cannot be empty")

    # Remove any whitespace
    namespace = namespace.strip()

    # Check length
    if len(namespace) > K8S_NAME_MAX_LENGTH:
        raise ValueError(
            f"Namespace name too long (max {K8S_NAME_MAX_LENGTH} characters)"
        )

    # Check format
    if not K8S_NAME_REGEX.match(namespace):
        raise ValueError(
            "Namespace must be lowercase alphanumeric characters or '-', "
            "and must start and end with alphanumeric character"
        )

    return namespace


def sanitize_command(command: str) -> str:
    """
    Sanitize shell command to prevent injection attacks.

    Args:
        command: Command to sanitize

    Returns:
        Sanitized command

    Raises:
        ValueError: If command contains dangerous patterns
    """
    if not command:
        raise ValueError("Command cannot be empty")

    # Dangerous patterns
    dangerous_patterns = [
        r"[;&|`$]",  # Command chaining
        r"<\(",  # Process substitution
        r">>",  # Append redirect
        r"<<",  # Here document
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            raise ValueError(
                f"Command contains potentially dangerous pattern: {pattern}"
            )

    return command.strip()


class ExperimentConfig(BaseModel):
    """Validated experiment configuration"""

    name: str = Field(..., description="Experiment name")
    namespace: str = Field(..., description="Kubernetes namespace")
    duration: int = Field(
        default=60, ge=1, le=3600, description="Experiment duration in seconds"
    )
    interval: Optional[int] = Field(
        default=None, ge=1, le=3600, description="Chaos interval in seconds"
    )
    timeout: int = Field(default=300, ge=1, le=7200, description="Timeout in seconds")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate experiment name"""
        return validate_experiment_name(v)

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, v):
        """Validate namespace"""
        return validate_namespace(v)

    @field_validator("duration", "interval", "timeout")
    @classmethod
    def validate_positive(cls, v):
        """Ensure positive values"""
        if v is not None and v <= 0:
            raise ValueError("Value must be positive")
        return v

    class Config:
        """Pydantic config"""

        extra = "forbid"  # Reject extra fields
        from_attributes = True


class ChaosEngineConfig(BaseModel):
    """Validated ChaosEngine configuration"""

    name: str
    namespace: str
    app_namespace: str
    app_label: str
    app_kind: str = "deployment"
    engine_state: str = "active"
    annotation_check: bool = False
    chaos_service_account: str = "litmus-admin"
    experiments: list = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return validate_experiment_name(v)

    @field_validator("namespace", "app_namespace")
    @classmethod
    def validate_namespace(cls, v):
        return validate_namespace(v)

    @field_validator("app_kind")
    @classmethod
    def validate_app_kind(cls, v):
        allowed = ["deployment", "statefulset", "daemonset"]
        if v.lower() not in allowed:
            raise ValueError(f"app_kind must be one of {allowed}")
        return v.lower()

    @field_validator("engine_state")
    @classmethod
    def validate_engine_state(cls, v):
        allowed = ["active", "stop"]
        if v.lower() not in allowed:
            raise ValueError(f"engine_state must be one of {allowed}")
        return v.lower()

    class Config:
        extra = "forbid"
