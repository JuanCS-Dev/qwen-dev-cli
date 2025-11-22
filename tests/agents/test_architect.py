"""
Tests for ArchitectAgent.

Tests cover:
    - Approval/veto decisions
    - JSON response parsing
    - READ_ONLY enforcement
    - Error handling
    - Integration with LLM/MCP
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock

from qwen_dev_cli.agents.architect import ArchitectAgent
from qwen_dev_cli.agents.base import AgentTask, AgentCapability


class TestArchitectAgentInitialization:
    """Test ArchitectAgent initialization."""

    def test_architect_initialization(self) -> None:
        """Test that Architect initializes with correct role and capabilities."""
        llm_client = MagicMock()
        mcp_client = MagicMock()

        architect = ArchitectAgent(llm_client, mcp_client)

        assert architect.role.value == "architect"
        assert AgentCapability.READ_ONLY in architect.capabilities
        assert len(architect.capabilities) == 1  # Only READ_ONLY
        assert "skeptical" in architect.system_prompt.lower()

    def test_architect_has_no_write_capabilities(self) -> None:
        """Test that Architect cannot use write tools."""
        architect = ArchitectAgent(MagicMock(), MagicMock())

        assert architect._can_use_tool("read_file") is True
        assert architect._can_use_tool("list_files") is True
        assert architect._can_use_tool("write_file") is False
        assert architect._can_use_tool("bash_command") is False
        assert architect._can_use_tool("git_commit") is False


class TestArchitectDecisions:
    """Test Architect approval/veto decisions."""

    @pytest.mark.asyncio
    async def test_architect_approves_good_request(self) -> None:
        """Test that Architect approves feasible requests."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "APPROVED",
                "reasoning": "Request is feasible and well-structured",
                "architecture": {
                    "approach": "Add JWT middleware to Express",
                    "risks": ["Token expiry management"],
                    "constraints": ["Requires jsonwebtoken package"],
                    "estimated_complexity": "MEDIUM",
                },
                "recommendations": ["Use RS256 algorithm", "Store secrets in env"],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Add JWT authentication to Express API",
            session_id="test-123",
        )

        response = await architect.execute(task)

        assert response.success is True
        assert response.data["decision"] == "APPROVED"
        assert "feasible" in response.reasoning.lower()
        assert response.metadata["decision"] == "APPROVED"
        assert response.metadata["complexity"] == "MEDIUM"

    @pytest.mark.asyncio
    async def test_architect_vetoes_bad_request(self) -> None:
        """Test that Architect vetoes impossible requests."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "VETOED",
                "reasoning": "Request requires unavailable quantum computing infrastructure",
                "architecture": {
                    "approach": "Not applicable",
                    "risks": ["Impossible with current tech"],
                    "constraints": ["Quantum hardware unavailable"],
                    "estimated_complexity": "HIGH",
                },
                "recommendations": ["Use classical algorithms instead"],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Implement quantum encryption for passwords",
            session_id="test-456",
        )

        response = await architect.execute(task)

        assert response.success is True
        assert response.data["decision"] == "VETOED"
        assert "quantum" in response.reasoning.lower() or "unavailable" in response.reasoning.lower()

    @pytest.mark.asyncio
    async def test_architect_handles_invalid_json(self) -> None:
        """Test that Architect handles non-JSON LLM responses gracefully."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value="The request looks good. I APPROVE this change."
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Add logging", session_id="test-789")

        response = await architect.execute(task)

        assert response.success is True  # Falls back to extraction
        assert response.data["decision"] in ("APPROVED", "UNKNOWN")

    @pytest.mark.asyncio
    async def test_architect_rejects_invalid_decision(self) -> None:
        """Test that Architect rejects responses with invalid decisions."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "MAYBE",  # Invalid
                "reasoning": "I'm not sure",
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")

        response = await architect.execute(task)

        assert response.success is False
        assert "must be APPROVED or VETOED" in response.error


class TestArchitectPromptBuilding:
    """Test Architect prompt construction."""

    def test_build_analysis_prompt_basic(self) -> None:
        """Test basic prompt construction."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Add caching layer",
            session_id="test",
        )

        prompt = architect._build_analysis_prompt(task)

        assert "Add caching layer" in prompt
        assert "REQUEST:" in prompt
        assert "CONTEXT:" in prompt

    def test_build_analysis_prompt_with_files(self) -> None:
        """Test prompt includes file context."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Refactor auth",
            session_id="test",
            context={
                "files": [
                    "src/auth.py",
                    "src/middleware.py",
                    "tests/test_auth.py",
                ],
            },
        )

        prompt = architect._build_analysis_prompt(task)

        assert "3 files" in prompt
        assert "src/auth.py" in prompt

    def test_build_analysis_prompt_with_constraints(self) -> None:
        """Test prompt includes constraints."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Migrate database",
            session_id="test",
            context={"constraints": "Zero downtime required"},
        )

        prompt = architect._build_analysis_prompt(task)

        assert "Zero downtime" in prompt
        assert "Constraints:" in prompt


class TestArchitectFallbackExtraction:
    """Test fallback decision extraction."""

    def test_extract_approved_decision(self) -> None:
        """Test extracting APPROVED from text."""
        architect = ArchitectAgent(MagicMock(), MagicMock())

        result = architect._extract_decision_fallback(
            "After careful analysis, I APPROVE this request."
        )

        assert result["decision"] == "APPROVED"
        assert "careful analysis" in result["reasoning"]

    def test_extract_vetoed_decision(self) -> None:
        """Test extracting VETOED from text."""
        architect = ArchitectAgent(MagicMock(), MagicMock())

        result = architect._extract_decision_fallback(
            "This request is VETOED due to high risk."
        )

        assert result["decision"] == "VETOED"
        assert "high risk" in result["reasoning"]

    def test_extract_unknown_decision(self) -> None:
        """Test extracting UNKNOWN when decision unclear."""
        architect = ArchitectAgent(MagicMock(), MagicMock())

        result = architect._extract_decision_fallback(
            "This is ambiguous and unclear."
        )

        assert result["decision"] == "UNKNOWN"


class TestArchitectErrorHandling:
    """Test Architect error handling."""

    @pytest.mark.asyncio
    async def test_architect_handles_llm_failure(self) -> None:
        """Test that Architect handles LLM failures gracefully."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(side_effect=Exception("LLM timeout"))

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")

        response = await architect.execute(task)

        assert response.success is False
        assert "failed" in response.reasoning.lower()
        assert "LLM timeout" in response.error

    @pytest.mark.asyncio
    async def test_architect_handles_missing_decision_field(self) -> None:
        """Test handling of malformed LLM response."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                # Missing "decision" field
                "reasoning": "Some reasoning",
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")

        response = await architect.execute(task)

        assert response.success is False
        assert "missing 'decision'" in response.reasoning.lower()
