#!/bin/bash

echo "🚀 Kubernetes Cluster Setup for Chaos Engineering Testing"
echo "========================================================"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first:"
    echo "   brew install kubectl"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install it first:"
    echo "   brew install helm"
    exit 1
fi

echo "✅ kubectl and helm are available"

# Check if Docker is running
if docker info &> /dev/null; then
    echo "✅ Docker is running"
    
    # Check if Kubernetes is enabled in Docker Desktop
    if kubectl cluster-info &> /dev/null; then
        echo "✅ Kubernetes cluster is available"
        echo "🎉 You're ready to test chaos experiments!"
        echo ""
        echo "Next steps:"
        echo "1. Run: python scripts/setup.py"
        echo "2. Run: python scripts/advanced-chaos-runner.py list"
        echo "3. Run: make phase2"
        exit 0
    else
        echo "⚠️  Docker is running but Kubernetes is not enabled"
        echo ""
        echo "To enable Kubernetes in Docker Desktop:"
        echo "1. Open Docker Desktop"
        echo "2. Go to Settings → Kubernetes"
        echo "3. Check 'Enable Kubernetes'"
        echo "4. Click 'Apply & Restart'"
        echo "5. Wait for Kubernetes to start"
        echo "6. Run this script again"
        exit 1
    fi
else
    echo "❌ Docker is not running"
    echo ""
    echo "Please start Docker Desktop and try again"
    exit 1
fi 