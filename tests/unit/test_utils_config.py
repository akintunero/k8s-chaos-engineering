"""
Unit tests for configuration management
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts.utils.config import Config, load_config


class TestConfig:
    """Tests for Config class"""
    
    def test_config_defaults(self):
        """Test default configuration values"""
        config = Config()
        
        assert config.app_namespace == "hello-world-app"
        assert config.litmus_namespace == "litmus"
        assert config.monitoring_namespace == "monitoring"
        assert config.default_timeout == 300
        assert config.retry_attempts == 3
    
    def test_config_custom_values(self):
        """Test custom configuration values"""
        config = Config(
            app_namespace="custom-app",
            default_timeout=600
        )
        
        assert config.app_namespace == "custom-app"
        assert config.default_timeout == 600
        assert config.litmus_namespace == "litmus"  # Default value
    
    def test_config_from_file(self, temp_config_file):
        """Test loading config from file"""
        config = Config.from_file(str(temp_config_file))
        
        assert config.app_namespace == "test-app"
        assert config.litmus_namespace == "test-litmus"
        assert config.monitoring_namespace == "test-monitoring"
        assert config.default_timeout == 60
    
    @patch.dict(os.environ, {'APP_NAMESPACE': 'env-app', 'DEFAULT_TIMEOUT': '500'})
    def test_config_env_override(self, temp_config_file):
        """Test environment variable overrides"""
        config = Config.from_file(str(temp_config_file))
        
        assert config.app_namespace == "env-app"  # Overridden by env
        assert config.default_timeout == 500  # Overridden by env
        assert config.litmus_namespace == "test-litmus"  # From file
    
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = Config(app_namespace="test")
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['app_namespace'] == "test"
        assert 'litmus_namespace' in config_dict


class TestLoadConfig:
    """Tests for load_config function"""
    
    def test_load_config_default(self):
        """Test loading default config"""
        # Use a non-existent path to force defaults
        config = load_config("/nonexistent/path.yaml")
        
        assert isinstance(config, Config)
        assert config.app_namespace == "hello-world-app"
    
    def test_load_config_from_file(self, temp_config_file):
        """Test loading config from specific file"""
        config = load_config(str(temp_config_file))
        
        assert config.app_namespace == "test-app"
