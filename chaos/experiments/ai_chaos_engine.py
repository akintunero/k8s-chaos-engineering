import numpy as np
from sklearn.ensemble import RandomForestClassifier
from litmuschaos.chaos.engine import ChaosEngine
from litmuschaos.chaos.experiment import Experiment
import logging

class AIChaosEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.chaos_engine = ChaosEngine()
        self.logger = logging.getLogger(__name__)

    def predict_failure_points(self, metrics_data):
        """
        Predict potential failure points using historical metrics
        """
        try:
            # Extract features from metrics
            features = self._extract_features(metrics_data)
            
            # Predict failure probability
            failure_probability = self.model.predict_proba(features)[:, 1]
            
            return failure_probability
        except Exception as e:
            self.logger.error(f"Error in failure prediction: {str(e)}")
            return None

    def generate_chaos_experiment(self, failure_probability, system_state):
        """
        Generate chaos experiment based on failure probability and system state
        """
        try:
            # Define experiment parameters based on predictions
            experiment_params = {
                'duration': self._calculate_duration(failure_probability),
                'severity': self._calculate_severity(failure_probability),
                'target_components': self._select_target_components(system_state)
            }

            # Create experiment
            experiment = Experiment(
                name=f"ai_generated_experiment_{np.random.randint(1000)}",
                namespace="litmus",
                parameters=experiment_params
            )

            return experiment
        except Exception as e:
            self.logger.error(f"Error in experiment generation: {str(e)}")
            return None

    def _extract_features(self, metrics_data):
        """
        Extract relevant features from metrics data
        """
        features = []
        for metric in metrics_data:
            features.extend([
                metric['cpu_usage'],
                metric['memory_usage'],
                metric['network_latency'],
                metric['error_rate']
            ])
        return np.array(features).reshape(1, -1)

    def _calculate_duration(self, failure_probability):
        """
        Calculate experiment duration based on failure probability
        """
        return int(300 * failure_probability)  # 5 minutes max

    def _calculate_severity(self, failure_probability):
        """
        Calculate experiment severity based on failure probability
        """
        if failure_probability > 0.8:
            return "high"
        elif failure_probability > 0.5:
            return "medium"
        return "low"

    def _select_target_components(self, system_state):
        """
        Select target components based on system state
        """
        components = []
        for component, state in system_state.items():
            if state['health_score'] < 0.7:
                components.append(component)
        return components

    def train_model(self, historical_data, failure_labels):
        """
        Train the AI model with historical data
        """
        try:
            features = self._extract_features(historical_data)
            self.model.fit(features, failure_labels)
            self.logger.info("Model training completed successfully")
        except Exception as e:
            self.logger.error(f"Error in model training: {str(e)}")

    def run_automated_experiment(self, metrics_data, system_state):
        """
        Run an automated chaos experiment
        """
        try:
            # Predict failure points
            failure_probability = self.predict_failure_points(metrics_data)
            
            if failure_probability is None:
                return None

            # Generate experiment
            experiment = self.generate_chaos_experiment(failure_probability, system_state)
            
            if experiment is None:
                return None

            # Run experiment
            result = self.chaos_engine.run_experiment(experiment)
            
            return {
                'experiment': experiment,
                'result': result,
                'failure_probability': failure_probability
            }
        except Exception as e:
            self.logger.error(f"Error in automated experiment: {str(e)}")
            return None 