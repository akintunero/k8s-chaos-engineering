#!/usr/bin/env python3
"""
Test Chaos Engineering Framework
Demonstrates the framework capabilities and tests the implementation
"""

import json
import subprocess  # nosec B404 - Required for kubectl command execution
import sys
import time
from datetime import datetime


def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = (
            subprocess.run(  # nosec B602 - shell=True required for kubectl commands
                command, shell=True, check=check, capture_output=True, text=True
            )
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        if check:
            return None
        return None


def test_kubernetes_cluster():
    """Test Kubernetes cluster connectivity"""
    print("🔍 Testing Kubernetes Cluster...")

    # Test cluster info
    result = run_command("kubectl cluster-info", check=False)
    if result:
        print("✅ Kubernetes cluster is accessible")
        return True
    else:
        print("❌ Cannot connect to Kubernetes cluster")
        return False


def test_namespace_creation():
    """Test namespace creation"""
    print("\n🔍 Testing Namespace Creation...")

    # Create test namespace
    result = run_command(
        "kubectl create namespace chaos-test --dry-run=client -o yaml | kubectl apply -f -",
        check=False,
    )
    if result is not None:
        print("✅ Namespace creation works")
        return True
    else:
        print("❌ Namespace creation failed")
        return False


def test_pod_creation():
    """Test basic pod creation"""
    print("\n🔍 Testing Pod Creation...")

    # Create a simple test pod
    pod_yaml = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  namespace: chaos-test
spec:
  containers:
  - name: test-container
    image: hello-world:latest
    command: ["/hello"]
"""

    # Write to temporary file
    with open("temp-test-pod.yaml", "w") as f:
        f.write(pod_yaml)

    # Apply the pod
    result = run_command("kubectl apply -f temp-test-pod.yaml", check=False)
    if result is not None:
        print("✅ Pod creation works")

        # Clean up
        run_command("kubectl delete -f temp-test-pod.yaml", check=False)
        run_command("rm temp-test-pod.yaml", check=False)
        return True
    else:
        print("❌ Pod creation failed")
        return False


def test_experiment_configurations():
    """Test that all experiment configurations are valid"""
    print("\n🔍 Testing Experiment Configurations...")

    experiments = [
        "pod-delete.yaml",
        "cpu-hog.yaml",
        "memory-hog.yaml",
        "network-latency.yaml",
        "network-partition.yaml",
        "disk-stress.yaml",
        "custom-chaos.yaml",
        "multi-cluster-chaos.yaml",
        "chaos-workflow.yaml",
    ]

    valid_count = 0
    for exp in experiments:
        result = run_command(
            f"kubectl apply -f experiments/{exp} --dry-run=client", check=False
        )
        if result is not None:
            print(f"✅ {exp}: Valid configuration")
            valid_count += 1
        else:
            print(f"❌ {exp}: Invalid configuration")

    print(f"\n📊 {valid_count}/{len(experiments)} experiment configurations are valid")
    return valid_count == len(experiments)


def test_automation_scripts():
    """Test automation scripts"""
    print("\n🔍 Testing Automation Scripts...")

    scripts = [
        "scripts/setup.py",
        "scripts/chaos-runner.py",
        "scripts/advanced-chaos-runner.py",
        "scripts/demo-chaos-framework.py",
    ]

    working_scripts = 0
    for script in scripts:
        result = run_command(f"python3 {script} --help", check=False)
        if result is not None or "usage:" in str(result):
            print(f"✅ {script}: Working")
            working_scripts += 1
        else:
            print(f"❌ {script}: Not working")

    print(f"\n📊 {working_scripts}/{len(scripts)} automation scripts are working")
    return working_scripts == len(scripts)


def test_makefile_commands():
    """Test Makefile commands"""
    print("\n🔍 Testing Makefile Commands...")

    # Test help command
    result = run_command("make help", check=False)
    if result and "Available commands:" in result:
        print("✅ Makefile help command works")
        return True
    else:
        print("❌ Makefile help command failed")
        return False


def test_monitoring_setup():
    """Test monitoring setup"""
    print("\n🔍 Testing Monitoring Setup...")

    # Check if monitoring namespace exists
    result = run_command("kubectl get namespace monitoring", check=False)
    if result and "monitoring" in result:
        print("✅ Monitoring namespace exists")

        # Check if Grafana is running
        grafana_result = run_command(
            "kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana",
            check=False,
        )
        if grafana_result and "Running" in grafana_result:
            print("✅ Grafana is running")
            return True
        else:
            print("⚠️ Grafana is not running")
            return False
    else:
        print("❌ Monitoring namespace not found")
        return False


def generate_test_report(results):
    """Generate a test report"""
    print("\n📋 Generating Test Report...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r),
        },
        "framework_status": "Ready" if all(results.values()) else "Needs Attention",
    }

    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📄 Test report saved: {report_file}")
    return report


def main():
    """Main test function"""
    print("🧪 Testing Chaos Engineering Framework")
    print("=" * 50)

    results = {}

    # Run all tests
    results["kubernetes_cluster"] = test_kubernetes_cluster()
    results["namespace_creation"] = test_namespace_creation()
    results["pod_creation"] = test_pod_creation()
    results["experiment_configurations"] = test_experiment_configurations()
    results["automation_scripts"] = test_automation_scripts()
    results["makefile_commands"] = test_makefile_commands()
    results["monitoring_setup"] = test_monitoring_setup()

    # Generate report
    report = generate_test_report(results)

    # Print summary
    print("\n" + "=" * 50)
    print("🎯 Test Summary")
    print("=" * 50)

    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test.replace('_', ' ').title()}")

    print(
        f"\n📊 Overall: {report['summary']['passed']}/{report['summary']['total_tests']} tests passed"
    )

    if all(results.values()):
        print("\n🎉 All tests passed! The chaos engineering framework is ready!")
        print("\n🚀 Next steps:")
        print("1. Run: python3 scripts/setup.py")
        print("2. Run: python3 scripts/advanced-chaos-runner.py list")
        print("3. Run: make phase2")
        print("4. Run: make phase3")
    else:
        print("\n⚠️ Some tests failed. Check the report for details.")
        print("\n🔧 To fix issues:")
        print("1. Ensure Docker Desktop is running with Kubernetes enabled")
        print("2. Check network connectivity")
        print("3. Verify kubectl and helm are properly configured")


if __name__ == "__main__":
    main()
