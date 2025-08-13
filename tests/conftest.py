"""
Pytest configuration and fixtures
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add scripts directory to path
import sys
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))


@pytest.fixture
def mock_config():
    """Mock configuration"""
    from scripts.utils.config import Config
    
    return Config(
        app_namespace="test-app",
        litmus_namespace="test-litmus",
        monitoring_namespace="test-monitoring",
        default_timeout=60,
        retry_attempts=2,
        retry_delay=1,
        check_interval=2
    )


@pytest.fixture
def mock_run_command():
    """Mock run_command function"""
    with patch('scripts.utils.k8s.run_command') as mock:
        yield mock


@pytest.fixture
def mock_kubectl():
    """Mock kubectl command output"""
    def _mock_kubectl(command, **kwargs):
        if 'get pods' in command:
            return {
                'items': [
                    {
                        'metadata': {'name': 'test-pod-1'},
                        'status': {
                            'phase': 'Running',
                            'conditions': [
                                {'type': 'Ready', 'status': 'True'}
                            ]
                        }
                    }
                ]
            }
        elif 'get deployment' in command:
            return {
                'status': {
                    'replicas': 1,
                    'readyReplicas': 1,
                    'conditions': [
                        {'type': 'Available', 'status': 'True'}
                    ]
                }
            }
        return {}
    
    return _mock_kubectl


@pytest.fixture
def temp_experiments_dir(tmp_path):
    """Temporary experiments directory"""
    exp_dir = tmp_path / "experiments"
    exp_dir.mkdir()
    return exp_dir


@pytest.fixture
def temp_config_file(tmp_path):
    """Temporary config file"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
namespaces:
  app: test-app
  litmus: test-litmus
  monitoring: test-monitoring
chaos:
  default_timeout: 60
  retry_attempts: 2
monitoring:
  enabled: true
""")
    return config_file
