"""
Pytest configuration for comprehensive E2E tests.

Author: JuanCS Dev
Date: 2025-11-27
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="jdev_e2e_comp_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_python_project(temp_project):
    """Create a sample Python project with multiple files."""
    # Create structure
    src_dir = temp_project / "src"
    src_dir.mkdir()
    tests_dir = temp_project / "tests"
    tests_dir.mkdir()

    # Create source files
    (src_dir / "__init__.py").write_text("")
    (src_dir / "main.py").write_text('''"""Main module."""

def greet(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b  # BUG: no zero check

class Calculator:
    """Simple calculator."""

    def __init__(self):
        self.history = []

    def calculate(self, op: str, a: float, b: float) -> float:
        """Perform calculation."""
        result = 0
        if op == "add":
            result = a + b
        elif op == "sub":
            result = a - b
        return result
''')

    (src_dir / "config.py").write_text('''"""Configuration."""

API_KEY = "sk-test123456789"  # Hardcoded secret
DATABASE_URL = "postgresql://user:pass@localhost/db"
DEBUG = True
''')

    (src_dir / "utils.py").write_text('''"""Utilities."""

def process_data(data):
    """Process data."""
    # TODO: add validation
    return data.upper()

def validate(value):
    """Validate value."""
    if not value:
        return False
    return True
''')

    # Create test files
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text('''"""Tests for main module."""

def test_greet():
    assert True

def test_add():
    assert True

def test_calculator():
    assert True
''')

    # Create README
    (temp_project / "README.md").write_text('''# Sample Project

This is a sample project for testing.
''')

    return temp_project
