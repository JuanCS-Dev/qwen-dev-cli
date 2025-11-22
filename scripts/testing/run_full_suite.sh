#!/bin/bash
# Comprehensive Test Suite Runner

set -euo pipefail

echo "🧪 Qwen Dev CLI - Full Test Suite"
echo "=================================="
echo ""

# Configuration
COVERAGE_THRESHOLD=80
PYTEST_ARGS="${PYTEST_ARGS:--v --tb=short}"

# Activate venv if exists
if [[ -d "venv" ]]; then
    source venv/bin/activate
fi

# Install test dependencies
echo "📦 Checking test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio pytest-timeout

# Run unit tests
echo ""
echo "🔬 Running unit tests..."
pytest tests/unit/ $PYTEST_ARGS --cov=qwen_dev_cli --cov-report=term-missing

# Run integration tests
echo ""
echo "🔗 Running integration tests..."
pytest tests/integration/ $PYTEST_ARGS

# Run E2E tests
echo ""
echo "🎯 Running end-to-end tests..."
pytest tests/e2e/ $PYTEST_ARGS --timeout=60

# Run bash command tests
echo ""
echo "⚡ Running bash hardening tests..."
pytest tests/test_bash_hardening.py $PYTEST_ARGS

# Coverage report
echo ""
echo "📊 Coverage Summary:"
pytest tests/ --cov=qwen_dev_cli --cov-report=term --cov-report=html

# Check coverage threshold
COVERAGE=$(pytest tests/ --cov=qwen_dev_cli --cov-report=term | grep "TOTAL" | awk '{print $NF}' | tr -d '%')
if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
    echo ""
    echo "❌ Coverage ${COVERAGE}% is below threshold ${COVERAGE_THRESHOLD}%"
    exit 1
fi

echo ""
echo "✅ All tests passed! Coverage: ${COVERAGE}%"
echo "📄 HTML report: htmlcov/index.html"
