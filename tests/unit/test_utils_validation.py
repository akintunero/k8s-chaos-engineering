"""
Unit tests for validation utilities
"""

import pytest

from scripts.utils.validation import (
    validate_experiment_name,
    validate_namespace,
    sanitize_command,
    ExperimentConfig,
    ChaosEngineConfig
)


class TestValidateExperimentName:
    """Tests for experiment name validation"""
    
    def test_valid_experiment_name(self):
        """Test valid experiment names"""
        assert validate_experiment_name("pod-delete") == "pod-delete"
        assert validate_experiment_name("cpu-hog-test") == "cpu-hog-test"
        assert validate_experiment_name("test123") == "test123"
    
    def test_invalid_experiment_name_empty(self):
        """Test empty experiment name"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_experiment_name("")
    
    def test_invalid_experiment_name_uppercase(self):
        """Test uppercase characters"""
        with pytest.raises(ValueError):
            validate_experiment_name("Pod-Delete")
    
    def test_invalid_experiment_name_special_chars(self):
        """Test special characters"""
        with pytest.raises(ValueError):
            validate_experiment_name("pod_delete")
        with pytest.raises(ValueError):
            validate_experiment_name("pod.delete")
    
    def test_invalid_experiment_name_starts_with_dash(self):
        """Test name starting with dash"""
        with pytest.raises(ValueError):
            validate_experiment_name("-pod-delete")
    
    def test_invalid_experiment_name_too_long(self):
        """Test name too long"""
        long_name = "a" * 254
        with pytest.raises(ValueError, match="too long"):
            validate_experiment_name(long_name)


class TestValidateNamespace:
    """Tests for namespace validation"""
    
    def test_valid_namespace(self):
        """Test valid namespaces"""
        assert validate_namespace("default") == "default"
        assert validate_namespace("hello-world-app") == "hello-world-app"
    
    def test_invalid_namespace_empty(self):
        """Test empty namespace"""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_namespace("")
    
    def test_invalid_namespace_uppercase(self):
        """Test uppercase characters"""
        with pytest.raises(ValueError):
            validate_namespace("Default")


class TestSanitizeCommand:
    """Tests for command sanitization"""
    
    def test_valid_command(self):
        """Test valid commands"""
        assert sanitize_command("kubectl get pods") == "kubectl get pods"
        assert sanitize_command("  kubectl apply -f file.yaml  ") == "kubectl apply -f file.yaml"
    
    def test_invalid_command_empty(self):
        """Test empty command"""
        with pytest.raises(ValueError):
            sanitize_command("")
    
    def test_invalid_command_semicolon(self):
        """Test command with semicolon"""
        with pytest.raises(ValueError, match="dangerous pattern"):
            sanitize_command("kubectl get pods; rm -rf /")
    
    def test_invalid_command_pipe(self):
        """Test command with pipe"""
        with pytest.raises(ValueError):
            sanitize_command("kubectl get pods | grep test")


class TestExperimentConfig:
    """Tests for ExperimentConfig model"""
    
    def test_valid_experiment_config(self):
        """Test valid experiment configuration"""
        config = ExperimentConfig(
            name="pod-delete",
            namespace="test-namespace",
            duration=60
        )
        
        assert config.name == "pod-delete"
        assert config.namespace == "test-namespace"
        assert config.duration == 60
    
    def test_invalid_experiment_name(self):
        """Test invalid experiment name"""
        with pytest.raises(ValueError):
            ExperimentConfig(
                name="Pod-Delete",  # Invalid: uppercase
                namespace="test-namespace"
            )
    
    def test_invalid_duration(self):
        """Test invalid duration"""
        with pytest.raises(ValueError):
            ExperimentConfig(
                name="pod-delete",
                namespace="test-namespace",
                duration=-1  # Invalid: negative
            )
    
    def test_experiment_config_defaults(self):
        """Test default values"""
        config = ExperimentConfig(
            name="pod-delete",
            namespace="test-namespace"
        )
        
        assert config.duration == 60
        assert config.timeout == 300


class TestChaosEngineConfig:
    """Tests for ChaosEngineConfig model"""
    
    def test_valid_chaos_engine_config(self):
        """Test valid ChaosEngine configuration"""
        config = ChaosEngineConfig(
            name="test-experiment",
            namespace="test-namespace",
            app_namespace="app-namespace",
            app_label="app=test"
        )
        
        assert config.name == "test-experiment"
        assert config.app_kind == "deployment"
        assert config.engine_state == "active"
    
    def test_invalid_app_kind(self):
        """Test invalid app_kind"""
        with pytest.raises(ValueError):
            ChaosEngineConfig(
                name="test",
                namespace="test",
                app_namespace="test",
                app_label="app=test",
                app_kind="invalid"
            )
