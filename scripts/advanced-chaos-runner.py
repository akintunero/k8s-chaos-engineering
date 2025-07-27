#!/usr/bin/env python3
"""
Advanced Chaos Experiment Runner
Manages Phase 2 and Phase 3 chaos experiments with enhanced features
"""

import subprocess
import sys
import time
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime

class AdvancedChaosRunner:
    def __init__(self):
        self.experiments_dir = Path("experiments")
        self.namespace = "hello-world-app"
        
    def run_command(self, command, check=True):
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {command}")
            print(f"Error: {e.stderr}")
            if check:
                sys.exit(1)
            return None

    def list_phase_experiments(self):
        """List experiments by phase"""
        experiments = {
            "Phase 1 - Basic Infrastructure": ["pod-delete"],
            "Phase 2 - Basic Chaos Experiments": ["cpu-hog", "memory-hog", "network-latency"],
            "Phase 3 - Advanced Chaos Experiments": ["network-partition", "disk-stress", "custom-chaos", "multi-cluster-chaos"],
            "Advanced Workflows": ["chaos-workflow"]
        }
        
        print("🎯 Available Chaos Experiments by Phase:")
        print("=" * 50)
        
        for phase, exps in experiments.items():
            print(f"\n{phase}:")
            for exp in exps:
                file_path = self.experiments_dir / f"{exp}.yaml"
                if file_path.exists():
                    print(f"  ✅ {exp}")
                else:
                    print(f"  ❌ {exp} (missing)")
        
        return experiments

    def run_phase_experiment(self, phase_name, experiment_name):
        """Run a specific phase experiment"""
        print(f"🚀 Running {phase_name}: {experiment_name}")
        
        # Apply the experiment
        result = self.run_command(f"kubectl apply -f experiments/{experiment_name}.yaml")
        print(f"✅ Applied experiment: {experiment_name}")
        
        # Wait for experiment to start
        print("⏳ Waiting for experiment to start...")
        time.sleep(15)
        
        # Monitor the experiment
        self.monitor_experiment(experiment_name)

    def run_comprehensive_workflow(self):
        """Run the comprehensive chaos workflow"""
        print("🎯 Running Comprehensive Chaos Workflow")
        print("This will execute multiple experiments in sequence...")
        
        workflow_file = "chaos-workflow.yaml"
        if not (self.experiments_dir / workflow_file).exists():
            print(f"❌ Workflow file {workflow_file} not found")
            return
        
        # Apply the workflow
        result = self.run_command(f"kubectl apply -f experiments/{workflow_file}")
        print(f"✅ Applied comprehensive workflow")
        
        # Monitor the workflow
        self.monitor_workflow()

    def monitor_experiment(self, experiment_name):
        """Monitor a running experiment"""
        print(f"📊 Monitoring experiment: {experiment_name}")
        
        # Check ChaosEngine status
        result = self.run_command(
            f"kubectl get chaosengine {experiment_name} -n {self.namespace} -o jsonpath='{{.status.engineStatus}}'", 
            check=False
        )
        if result:
            print(f"Engine Status: {result}")
        
        # Check for chaos pods
        result = self.run_command(f"kubectl get pods -n {self.namespace} -l job-name", check=False)
        if result:
            print("Chaos Pods:")
            print(result)
        
        # Check application pods
        result = self.run_command(f"kubectl get pods -n {self.namespace}", check=False)
        if result:
            print("Application Pods:")
            print(result)

    def monitor_workflow(self):
        """Monitor the comprehensive workflow"""
        print("📊 Monitoring comprehensive workflow...")
        
        # Check all chaos engines
        result = self.run_command(f"kubectl get chaosengine -n {self.namespace}", check=False)
        if result:
            print("Active Chaos Engines:")
            print(result)
        
        # Check application health
        result = self.run_command(f"kubectl get pods -n {self.namespace} -l app=flask-app", check=False)
        if result:
            print("Application Pods Status:")
            print(result)

    def run_phase_2_experiments(self):
        """Run all Phase 2 experiments"""
        print("🎯 Running Phase 2: Basic Chaos Experiments")
        
        phase_2_experiments = ["pod-delete", "cpu-hog", "memory-hog", "network-latency"]
        
        for exp in phase_2_experiments:
            if (self.experiments_dir / f"{exp}.yaml").exists():
                print(f"\n--- Running {exp} ---")
                self.run_phase_experiment("Phase 2", exp)
                time.sleep(30)  # Wait between experiments
            else:
                print(f"❌ Experiment {exp} not found")

    def run_phase_3_experiments(self):
        """Run all Phase 3 experiments"""
        print("🎯 Running Phase 3: Advanced Chaos Experiments")
        
        phase_3_experiments = ["network-partition", "disk-stress", "custom-chaos"]
        
        for exp in phase_3_experiments:
            if (self.experiments_dir / f"{exp}.yaml").exists():
                print(f"\n--- Running {exp} ---")
                self.run_phase_experiment("Phase 3", exp)
                time.sleep(45)  # Wait longer between advanced experiments
            else:
                print(f"❌ Experiment {exp} not found")

    def generate_experiment_report(self):
        """Generate a report of all experiments"""
        print("📋 Generating Chaos Experiment Report")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "namespace": self.namespace,
            "experiments": {}
        }
        
        # Get all chaos engines
        result = self.run_command(f"kubectl get chaosengine -n {self.namespace} -o json", check=False)
        if result:
            engines = json.loads(result)
            for engine in engines.get('items', []):
                name = engine['metadata']['name']
                status = engine.get('status', {})
                report['experiments'][name] = {
                    "status": status.get('engineStatus', 'Unknown'),
                    "experiments": status.get('experiments', [])
                }
        
        # Get application status
        result = self.run_command(f"kubectl get pods -n {self.namespace} -l app=flask-app -o json", check=False)
        if result:
            pods = json.loads(result)
            report['application'] = {
                "total_pods": len(pods.get('items', [])),
                "ready_pods": len([p for p in pods.get('items', []) if p['status']['phase'] == 'Running'])
            }
        
        # Save report
        report_file = f"chaos_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report saved to {report_file}")
        return report

    def cleanup_all_experiments(self):
        """Clean up all chaos experiments"""
        print("🧹 Cleaning up all chaos experiments...")
        
        # Get all chaos engines
        result = self.run_command(f"kubectl get chaosengine -n {self.namespace} -o jsonpath='{{.items[*].metadata.name}}'", check=False)
        if result:
            experiments = result.split()
            for exp in experiments:
                print(f"Stopping experiment: {exp}")
                self.run_command(f"kubectl patch chaosengine {exp} -n {self.namespace} --type='merge' -p '{{\"spec\":{{\"engineState\":\"stop\"}}}}'")
                self.run_command(f"kubectl delete chaosengine {exp} -n {self.namespace}")
        else:
            print("No experiments to clean up")

def main():
    parser = argparse.ArgumentParser(description="Advanced Chaos Experiment Runner")
    parser.add_argument("action", choices=[
        "list", "phase2", "phase3", "workflow", "report", "cleanup", "run"
    ], help="Action to perform")
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
            print("Please specify an experiment with --experiment")
            sys.exit(1)
        runner.run_phase_experiment("Custom", args.experiment)

if __name__ == "__main__":
    main() 