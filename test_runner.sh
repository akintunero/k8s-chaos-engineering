#!/bin/bash
# Test runner script for CI/CD

set -e

echo "🧪 Running Chaos Engineering Framework Tests"
echo "=============================================="

# Set up Python path
export PYTHONPATH=$PWD/scripts:$PYTHONPATH

# Install dependencies
echo "📦 Installing dependencies..."
cd scripts
pip install -q -r requirements.txt -r requirements-dev.txt
cd ..

# Run tests
echo "🚀 Running tests..."
python3 -m pytest tests/ -v --tb=short --no-cov

# Run linting (if available)
if command -v black &> /dev/null; then
    echo "🔍 Running black..."
    black --check scripts/ || echo "Black check failed (non-blocking)"
fi

if command -v flake8 &> /dev/null; then
    echo "🔍 Running flake8..."
    flake8 scripts/ --max-line-length=127 --extend-ignore=E203 || echo "Flake8 check failed (non-blocking)"
fi

echo "✅ Tests completed!"
