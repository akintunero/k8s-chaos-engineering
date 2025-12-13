"""
Unit tests for Kubernetes utilities
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import json

from scripts.utils.k8s import (
    run_command,
    wait_for_pods,
    wait_for_deployment,
    retry_with_backoff,
    KubernetesError,
    TimeoutError
)


class TestRunCommand:
    """Tests for run_command function"""
    
    @patch('scripts.utils.k8s.subprocess.run')
    def test_run_command_success(self, mock_subprocess):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_subprocess.return_value = mock_result
        
        result = run_command("echo test", check=True)
        assert result == "test output"
        mock_subprocess.assert_called_once()
    
    @patch('scripts.utils.k8s.subprocess.run')
    def test_run_command_failure_with_retry(self, mock_subprocess):
        """Test command failure with retries"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "error"
        mock_subprocess.return_value = mock_result
        
        with pytest.raises(KubernetesError):
            run_command("false", check=True, retries=2)
        
        assert mock_subprocess.call_count == 2
    
    @patch('scripts.utils.k8s.subprocess.run')
    def test_run_command_no_check(self, mock_subprocess):
        """Test command failure without check"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "error"
        mock_subprocess.return_value = mock_result
        
        result = run_command("false", check=False)
        assert result is None


class TestWaitForPods:
    """Tests for wait_for_pods function"""
    
    @patch('scripts.utils.k8s.run_command')
    def test_wait_for_pods_success(self, mock_run_command):
        """Test successful pod wait"""
        pods_json = {
            'items': [
                {
                    'status': {
                        'phase': 'Running',
                        'conditions': [
                            {'type': 'Ready', 'status': 'True'}
                        ]
                    }
                }
            ]
        }
        
        mock_run_command.return_value = json.dumps(pods_json)
        
        result = wait_for_pods("test-namespace", timeout=10, check_interval=1)
        assert result is True
    
    @patch('scripts.utils.k8s.run_command')
    def test_wait_for_pods_timeout(self, mock_run_command):
        """Test pod wait timeout"""
        mock_run_command.return_value = json.dumps({'items': []})
        
        with pytest.raises(TimeoutError):
            wait_for_pods("test-namespace", timeout=2, check_interval=1)
    
    @patch('scripts.utils.k8s.run_command')
    def test_wait_for_pods_with_label_selector(self, mock_run_command):
        """Test pod wait with label selector"""
        pods_json = {
            'items': [
                {
                    'status': {
                        'phase': 'Running',
                        'conditions': [
                            {'type': 'Ready', 'status': 'True'}
                        ]
                    }
                }
            ]
        }
        
        mock_run_command.return_value = json.dumps(pods_json)
        
        result = wait_for_pods("test-namespace", label_selector="app=test", timeout=10, check_interval=1)
        assert result is True
        # Verify label selector was used
        assert '-l app=test' in mock_run_command.call_args[0][0]


class TestWaitForDeployment:
    """Tests for wait_for_deployment function"""
    
    @patch('scripts.utils.k8s.run_command')
    def test_wait_for_deployment_success(self, mock_run_command):
        """Test successful deployment wait"""
        deployment_json = {
            'status': {
                'replicas': 2,
                'readyReplicas': 2,
                'conditions': [
                    {'type': 'Available', 'status': 'True'}
                ]
            }
        }
        
        mock_run_command.return_value = json.dumps(deployment_json)
        
        result = wait_for_deployment("test-namespace", "test-deployment", timeout=10, check_interval=1)
        assert result is True
    
    @patch('scripts.utils.k8s.run_command')
    def test_wait_for_deployment_timeout(self, mock_run_command):
        """Test deployment wait timeout"""
        mock_run_command.return_value = None
        
        with pytest.raises(TimeoutError):
            wait_for_deployment("test-namespace", "test-deployment", timeout=2, check_interval=1)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff function"""
    
    def test_retry_with_backoff_success(self):
        """Test successful function execution"""
        func = Mock(return_value="success")
        
        result = retry_with_backoff(func, max_attempts=3)
        
        assert result == "success"
        assert func.call_count == 1
    
    def test_retry_with_backoff_retry_success(self):
        """Test retry that eventually succeeds"""
        func = Mock(side_effect=[Exception("fail"), Exception("fail"), "success"])
        
        result = retry_with_backoff(func, max_attempts=3, base_delay=0.1)
        
        assert result == "success"
        assert func.call_count == 3
    
    def test_retry_with_backoff_all_fail(self):
        """Test retry that fails all attempts"""
        func = Mock(side_effect=Exception("fail"))
        
        with pytest.raises(Exception):
            retry_with_backoff(func, max_attempts=3, base_delay=0.1)
