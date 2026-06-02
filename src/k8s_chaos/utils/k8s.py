"""
Kubernetes utility functions with proper error handling and retries
"""

import json
import subprocess  # nosec B404 - Required for kubectl command execution
import sys
import time
from typing import Any, Dict, List, Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .logging import get_logger

logger = get_logger(__name__)


class KubernetesError(Exception):
    """Custom exception for Kubernetes operations"""

    pass


class TimeoutError(Exception):
    """Custom exception for timeout operations"""

    pass


def run_command(
    command: str,
    check: bool = True,
    timeout: Optional[int] = None,
    retries: int = 3,
    retry_delay: int = 1,
) -> Optional[str]:
    """
    Run a shell command with retry logic and proper error handling.

    Args:
        command: Shell command to execute
        check: If True, raise exception on failure
        timeout: Command timeout in seconds
        retries: Number of retry attempts
        retry_delay: Initial delay between retries (exponential backoff)

    Returns:
        Command output as string, or None on failure

    Raises:
        KubernetesError: If command fails and check=True
    """
    last_error = None

    for attempt in range(retries):
        try:
            result = (
                subprocess.run(  # nosec B602 - shell=True required for kubectl commands
                    command,
                    shell=True,
                    check=check,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                last_error = result.stderr
                logger.warning(
                    f"Command failed (attempt {attempt + 1}/{retries}): {command}"
                )
                logger.debug(f"Error: {result.stderr}")

                if attempt < retries - 1:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    if check:
                        raise KubernetesError(
                            f"Command failed after {retries} attempts: {command}\nError: {last_error}"
                        )
                    return None

        except subprocess.TimeoutExpired as e:
            last_error = f"Command timed out after {timeout} seconds"
            logger.error(last_error)
            if check:
                raise TimeoutError(last_error)
            return None

        except subprocess.CalledProcessError as e:
            last_error = e.stderr
            logger.warning(
                f"Command failed (attempt {attempt + 1}/{retries}): {command}"
            )
            logger.debug(f"Error: {e.stderr}")

            if attempt < retries - 1:
                delay = retry_delay * (2**attempt)
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                if check:
                    raise KubernetesError(
                        f"Command failed after {retries} attempts: {command}\nError: {last_error}"
                    )
                return None

    return None


def wait_for_pods(
    namespace: str,
    label_selector: Optional[str] = None,
    timeout: int = 300,
    check_interval: int = 5,
    expected_count: Optional[int] = None,
) -> bool:
    """
    Wait for pods to be ready using polling instead of hard-coded sleeps.

    Args:
        namespace: Kubernetes namespace
        label_selector: Label selector for pods (e.g., "app=flask-app")
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        expected_count: Expected number of pods (optional)

    Returns:
        True if pods are ready, False on timeout

    Raises:
        TimeoutError: If pods are not ready within timeout
    """
    """
    Wait for pods to be ready using polling instead of hard-coded sleeps.
    
    Args:
        namespace: Kubernetes namespace
        label_selector: Label selector for pods (e.g., "app=flask-app")
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        expected_count: Expected number of pods (optional)
    
    Returns:
        True if pods are ready, False on timeout
    
    Raises:
        TimeoutError: If pods are not ready within timeout
    """
    logger.info(f"Waiting for pods in namespace '{namespace}' (timeout: {timeout}s)")

    if label_selector:
        logger.debug(f"Using label selector: {label_selector}")

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Build kubectl command
            cmd = f"kubectl get pods -n {namespace}"
            if label_selector:
                cmd += f" -l {label_selector}"
            cmd += " -o json"

            result = run_command(cmd, check=False)
            if not result:
                logger.debug("No pods found yet, waiting...")
                time.sleep(check_interval)
                continue

            pods_data = json.loads(result)
            pods = pods_data.get("items", [])

            if expected_count and len(pods) != expected_count:
                logger.debug(
                    f"Pod count mismatch: expected {expected_count}, found {len(pods)}"
                )
                time.sleep(check_interval)
                continue

            # Check if all pods are ready
            ready_count = 0
            for pod in pods:
                status = pod.get("status", {})
                phase = status.get("phase", "")
                conditions = status.get("conditions", [])

                # Check if pod is running
                if phase == "Running":
                    # Check ready condition
                    for condition in conditions:
                        if (
                            condition.get("type") == "Ready"
                            and condition.get("status") == "True"
                        ):
                            ready_count += 1
                            break

            if expected_count:
                if ready_count == expected_count:
                    logger.info(f"✅ All {ready_count} pods are ready")
                    return True
            else:
                if ready_count > 0 and ready_count == len(pods):
                    logger.info(f"✅ All {ready_count} pods are ready")
                    return True

            logger.debug(f"Pods ready: {ready_count}/{len(pods)}, waiting...")
            time.sleep(check_interval)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse pod JSON: {e}")
            time.sleep(check_interval)
        except Exception as e:
            logger.error(f"Error checking pods: {e}")
            time.sleep(check_interval)

    elapsed = time.time() - start_time
    error_msg = f"Timeout waiting for pods in namespace '{namespace}' after {elapsed:.0f} seconds"
    logger.error(error_msg)
    raise TimeoutError(error_msg)


def wait_for_deployment(
    namespace: str, deployment_name: str, timeout: int = 300, check_interval: int = 5
) -> bool:
    """
    Wait for a deployment to be ready.

    Args:
        namespace: Kubernetes namespace
        deployment_name: Name of the deployment
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        True if deployment is ready

    Raises:
        TimeoutError: If deployment is not ready within timeout
    """
    logger.info(
        f"Waiting for deployment '{deployment_name}' in namespace '{namespace}'"
    )

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            cmd = f"kubectl get deployment {deployment_name} -n {namespace} -o json"
            result = run_command(cmd, check=False)

            if not result:
                logger.debug("Deployment not found yet, waiting...")
                time.sleep(check_interval)
                continue

            deployment = json.loads(result)
            status = deployment.get("status", {})

            # Check if deployment is ready
            ready_replicas = status.get("readyReplicas", 0)
            replicas = status.get("replicas", 0)
            conditions = status.get("conditions", [])

            # Check for available condition
            available = False
            for condition in conditions:
                if (
                    condition.get("type") == "Available"
                    and condition.get("status") == "True"
                ):
                    available = True
                    break

            if available and ready_replicas == replicas and replicas > 0:
                logger.info(
                    f"✅ Deployment '{deployment_name}' is ready ({ready_replicas}/{replicas} replicas)"
                )
                return True

            logger.debug(
                f"Deployment status: {ready_replicas}/{replicas} replicas ready, waiting..."
            )
            time.sleep(check_interval)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse deployment JSON: {e}")
            time.sleep(check_interval)
        except Exception as e:
            logger.error(f"Error checking deployment: {e}")
            time.sleep(check_interval)

    elapsed = time.time() - start_time
    error_msg = f"Timeout waiting for deployment '{deployment_name}' after {elapsed:.0f} seconds"
    logger.error(error_msg)
    raise TimeoutError(error_msg)


def retry_with_backoff(
    func,
    max_attempts: int = 3,
    base_delay: int = 1,
    max_delay: int = 60,
    exceptions: tuple = (Exception,),
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Function return value

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                delay = min(base_delay * (2**attempt), max_delay)
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All {max_attempts} attempts failed")
                raise

    if last_exception:
        raise last_exception
