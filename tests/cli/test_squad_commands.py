"""Tests for CLI squad and workflow commands."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typer.testing import CliRunner
from qwen_dev_cli.cli import app
from qwen_dev_cli.orchestration.squad import WorkflowResult, WorkflowStatus

runner = CliRunner()

@pytest.fixture
def mock_squad():
    with patch("qwen_dev_cli.cli.get_squad") as mock:
        squad_instance = MagicMock()
        # Mock execute_workflow to return a dummy result
        result = WorkflowResult(
            request="test",
            status=WorkflowStatus.COMPLETED
        )
        squad_instance.execute_workflow = AsyncMock(return_value=result)
        squad_instance.get_phase_summary.return_value = "Workflow Completed Successfully"
        mock.return_value = squad_instance
        yield mock

def test_squad_run_command(mock_squad):
    """Test 'qwen-dev squad run' command."""
    result = runner.invoke(app, ["squad", "run", "Create a hello world script"])
    assert result.exit_code == 0
    assert "DevSquad Mission" in result.stdout
    assert "Create a hello world script" in result.stdout
    assert "Workflow Completed Successfully" in result.stdout

def test_squad_status_command():
    """Test 'qwen-dev squad status' command."""
    result = runner.invoke(app, ["squad", "status"])
    assert result.exit_code == 0
    assert "DevSquad Agent Status" in result.stdout
    assert "Architect" in result.stdout
    assert "Architecture Analysis" in result.stdout

def test_workflow_list_command():
    """Test 'qwen-dev workflow list' command."""
    result = runner.invoke(app, ["workflow", "list"])
    assert result.exit_code == 0
    assert "Available Workflows" in result.stdout
    assert "setup-fastapi" in result.stdout
    assert "add-auth" in result.stdout

def test_workflow_run_command(mock_squad):
    """Test 'qwen-dev workflow run' command."""
    # Inputs: project_name, python_version, confirmation
    result = runner.invoke(app, ["workflow", "run", "setup-fastapi"], input="my-api\n3.11\ny\n")
    assert result.exit_code == 0
    assert "Starting Workflow" in result.stdout
    assert "setup-fastapi" in result.stdout
    assert "Execution Plan" in result.stdout
    assert "Workflow Completed Successfully" in result.stdout

def test_workflow_run_invalid():
    """Test 'qwen-dev workflow run' with invalid workflow."""
    result = runner.invoke(app, ["workflow", "run", "invalid-workflow"])
    assert result.exit_code == 1
    assert "Workflow 'invalid-workflow' not found" in result.stdout
