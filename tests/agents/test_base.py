"""
Tests for BaseAgent foundation.

Tests cover:
    - Role and capability enforcement
    - Tool validation
    - LLM and MCP integration
    - Error handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from qwen_dev_cli.agents.base import (
    AgentCapability,
    AgentRole,
    AgentTask,
    AgentResponse,
    BaseAgent,
    CapabilityViolationError,
)


class TestAgentEnums:
    """Test agent role and capability enums."""

    def test_agent_roles_defined(self) -> None:
        """Test all agent roles are properly defined."""
        assert AgentRole.ARCHITECT == "architect"
        assert AgentRole.EXPLORER == "explorer"
        assert AgentRole.PLANNER == "planner"
        assert AgentRole.REFACTORER == "refactorer"
        assert AgentRole.REVIEWER == "reviewer"

    def test_agent_capabilities_defined(self) -> None:
        """Test all agent capabilities are properly defined."""
        assert AgentCapability.READ_ONLY == "read_only"
        assert AgentCapability.FILE_EDIT == "file_edit"
        assert AgentCapability.BASH_EXEC == "bash_exec"
        assert AgentCapability.GIT_OPS == "git_ops"
        assert AgentCapability.DESIGN == "design"


class TestAgentTask:
    """Test AgentTask Pydantic model."""

    def test_task_creation_minimal(self) -> None:
        """Test task creation with minimal required fields."""
        task = AgentTask(
            request="Add JWT authentication",
            session_id="test-session-123",
        )

        assert task.request == "Add JWT authentication"
        assert task.session_id == "test-session-123"
        assert task.task_id  # Auto-generated UUID
        assert isinstance(task.context, dict)
        assert isinstance(task.metadata, dict)

    def test_task_creation_full(self) -> None:
        """Test task creation with all fields."""
        task = AgentTask(
            request="Migrate to FastAPI",
            session_id="test-session-456",
            context={"files": ["app.py", "routes.py"]},
            metadata={"priority": "high"},
        )

        assert task.request == "Migrate to FastAPI"
        assert task.context["files"] == ["app.py", "routes.py"]
        assert task.metadata["priority"] == "high"

    def test_task_immutable(self) -> None:
        """Test that tasks are immutable after creation."""
        task = AgentTask(request="Test", session_id="test")

        with pytest.raises(Exception):  # Pydantic ValidationError
            task.request = "Modified"  # type: ignore

    def test_task_requires_request(self) -> None:
        """Test that request field is required."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AgentTask(session_id="test")  # type: ignore


class TestAgentResponse:
    """Test AgentResponse Pydantic model."""

    def test_response_success(self) -> None:
        """Test successful response creation."""
        response = AgentResponse(
            success=True,
            reasoning="Plan generated successfully",
            data={"steps": 5, "estimated_time": "10m"},
        )

        assert response.success is True
        assert response.error is None
        assert response.data["steps"] == 5
        assert response.timestamp  # Auto-generated

    def test_response_failure(self) -> None:
        """Test failure response creation."""
        response = AgentResponse(
            success=False,
            reasoning="Invalid project structure",
            error="No pyproject.toml found",
        )

        assert response.success is False
        assert response.error == "No pyproject.toml found"


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Dummy implementation."""
        return AgentResponse(
            success=True,
            reasoning="Test execution",
        )


class TestBaseAgent:
    """Test BaseAgent abstract class."""

    def test_agent_initialization(self) -> None:
        """Test agent initialization with required parameters."""
        llm_client = MagicMock()
        mcp_client = MagicMock()

        agent = ConcreteAgent(
            role=AgentRole.ARCHITECT,
            capabilities=[AgentCapability.READ_ONLY],
            llm_client=llm_client,
            mcp_client=mcp_client,
            system_prompt="You are an architect",
        )

        assert agent.role == AgentRole.ARCHITECT
        assert AgentCapability.READ_ONLY in agent.capabilities
        assert agent.execution_count == 0
        assert agent.system_prompt == "You are an architect"

    def test_can_use_tool_read_only(self) -> None:
        """Test READ_ONLY capability allows read tools."""
        agent = ConcreteAgent(
            role=AgentRole.ARCHITECT,
            capabilities=[AgentCapability.READ_ONLY],
            llm_client=MagicMock(),
            mcp_client=MagicMock(),
        )

        assert agent._can_use_tool("read_file") is True
        assert agent._can_use_tool("list_files") is True
        assert agent._can_use_tool("grep_search") is True
        assert agent._can_use_tool("write_file") is False
        assert agent._can_use_tool("bash_command") is False

    def test_can_use_tool_file_edit(self) -> None:
        """Test FILE_EDIT capability allows file modification."""
        agent = ConcreteAgent(
            role=AgentRole.REFACTORER,
            capabilities=[AgentCapability.FILE_EDIT],
            llm_client=MagicMock(),
            mcp_client=MagicMock(),
        )

        assert agent._can_use_tool("write_file") is True
        assert agent._can_use_tool("edit_file") is True
        assert agent._can_use_tool("delete_file") is True
        assert agent._can_use_tool("read_file") is False

    def test_can_use_tool_multiple_capabilities(self) -> None:
        """Test agent with multiple capabilities."""
        agent = ConcreteAgent(
            role=AgentRole.REFACTORER,
            capabilities=[
                AgentCapability.READ_ONLY,
                AgentCapability.FILE_EDIT,
                AgentCapability.BASH_EXEC,
            ],
            llm_client=MagicMock(),
            mcp_client=MagicMock(),
        )

        assert agent._can_use_tool("read_file") is True
        assert agent._can_use_tool("write_file") is True
        assert agent._can_use_tool("bash_command") is True
        assert agent._can_use_tool("git_commit") is False

    @pytest.mark.asyncio
    async def test_call_llm_basic(self) -> None:
        """Test LLM call wrapper."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(return_value="LLM response")

        agent = ConcreteAgent(
            role=AgentRole.PLANNER,
            capabilities=[AgentCapability.DESIGN],
            llm_client=llm_client,
            mcp_client=MagicMock(),
            system_prompt="You are a planner",
        )

        response = await agent._call_llm("Generate a plan")

        assert response == "LLM response"
        llm_client.generate.assert_called_once()
        assert agent.execution_count == 1

    @pytest.mark.asyncio
    async def test_execute_tool_with_capability(self) -> None:
        """Test tool execution with valid capability."""
        mcp_client = MagicMock()
        mcp_client.call_tool = AsyncMock(return_value={"content": "file.py"})

        agent = ConcreteAgent(
            role=AgentRole.EXPLORER,
            capabilities=[AgentCapability.READ_ONLY],
            llm_client=MagicMock(),
            mcp_client=mcp_client,
        )

        result = await agent._execute_tool("read_file", {"path": "test.py"})

        assert result["content"] == "file.py"
        mcp_client.call_tool.assert_called_once_with(
            tool_name="read_file",
            arguments={"path": "test.py"},
        )

    @pytest.mark.asyncio
    async def test_execute_tool_without_capability_raises(self) -> None:
        """Test tool execution without capability raises error."""
        agent = ConcreteAgent(
            role=AgentRole.ARCHITECT,
            capabilities=[AgentCapability.READ_ONLY],  # No FILE_EDIT
            llm_client=MagicMock(),
            mcp_client=MagicMock(),
        )

        with pytest.raises(CapabilityViolationError) as exc_info:
            await agent._execute_tool("write_file", {"path": "test.py"})

        assert "cannot use tool 'write_file'" in str(exc_info.value)
        assert "architect" in str(exc_info.value)

    def test_agent_repr(self) -> None:
        """Test agent string representation."""
        agent = ConcreteAgent(
            role=AgentRole.REVIEWER,
            capabilities=[AgentCapability.READ_ONLY, AgentCapability.GIT_OPS],
            llm_client=MagicMock(),
            mcp_client=MagicMock(),
        )

        repr_str = repr(agent)
        assert "ConcreteAgent" in repr_str
        assert "reviewer" in repr_str
        assert "read_only" in repr_str
        assert "git_ops" in repr_str
        assert "executions=0" in repr_str
