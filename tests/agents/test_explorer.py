"""
Tests for ExplorerAgent.

Tests cover:
    - File discovery and search
    - Token budget awareness
    - File limit enforcement
    - JSON response parsing
    - Fallback extraction
    - READ_ONLY enforcement
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock

from qwen_dev_cli.agents.explorer import ExplorerAgent
from qwen_dev_cli.agents.base import AgentTask, AgentCapability


class TestExplorerAgentInitialization:
    """Test ExplorerAgent initialization."""

    def test_explorer_initialization(self) -> None:
        """Test that Explorer initializes with correct role and capabilities."""
        llm_client = MagicMock()
        mcp_client = MagicMock()

        explorer = ExplorerAgent(llm_client, mcp_client)

        assert explorer.role.value == "explorer"
        assert AgentCapability.READ_ONLY in explorer.capabilities
        assert len(explorer.capabilities) == 1  # Only READ_ONLY
        assert "token budget" in explorer.system_prompt.lower()

    def test_explorer_has_no_write_capabilities(self) -> None:
        """Test that Explorer cannot use write tools."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())

        assert explorer._can_use_tool("read_file") is True
        assert explorer._can_use_tool("grep_search") is True
        assert explorer._can_use_tool("find_files") is True
        assert explorer._can_use_tool("write_file") is False
        assert explorer._can_use_tool("bash_command") is False


class TestExplorerFileDiscovery:
    """Test Explorer file discovery functionality."""

    @pytest.mark.asyncio
    async def test_explorer_finds_relevant_files(self) -> None:
        """Test that Explorer returns relevant files."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {
                        "path": "src/auth/jwt.py",
                        "relevance": "HIGH",
                        "reason": "Contains JWT validation logic",
                        "key_symbols": ["verify_token", "decode_token"],
                    },
                    {
                        "path": "src/api/auth_routes.py",
                        "relevance": "HIGH",
                        "reason": "Auth API endpoints",
                        "key_symbols": ["login", "logout"],
                    },
                ],
                "dependencies": [
                    {"from": "auth_routes.py", "to": "jwt.py", "type": "imports"}
                ],
                "context_summary": "Found 2 auth-related files",
                "token_estimate": 3000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Find authentication files",
            session_id="test-123",
        )

        response = await explorer.execute(task)

        assert response.success is True
        assert len(response.data["relevant_files"]) == 2
        assert response.data["relevant_files"][0]["path"] == "src/auth/jwt.py"
        assert response.metadata["file_count"] == 2
        assert response.metadata["token_estimate"] == 3000
        assert response.metadata["within_budget"] is True

    @pytest.mark.asyncio
    async def test_explorer_enforces_max_files_limit(self) -> None:
        """Test that Explorer respects max_files limit."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": f"file{i}.py", "relevance": "MEDIUM", "reason": "Test"}
                    for i in range(20)  # 20 files returned
                ],
                "dependencies": [],
                "context_summary": "Found many files",
                "token_estimate": 10000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Find all Python files",
            session_id="test-456",
            context={"max_files": 5},  # Limit to 5
        )

        response = await explorer.execute(task)

        assert response.success is True
        assert len(response.data["relevant_files"]) == 5  # Enforced limit
        assert response.metadata["file_count"] == 5

    @pytest.mark.asyncio
    async def test_explorer_calculates_token_estimate(self) -> None:
        """Test that Explorer estimates token usage."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": f"file{i}.py", "relevance": "LOW", "reason": "Test"}
                    for i in range(10)
                ],
                "dependencies": [],
                "context_summary": "10 files",
                # No token_estimate provided - should calculate
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)

        assert response.success is True
        # Should calculate: 10 files * 200 tokens = 2000
        assert response.metadata["token_estimate"] == 2000


class TestExplorerTokenBudgetAwareness:
    """Test Explorer token budget tracking."""

    @pytest.mark.asyncio
    async def test_explorer_flags_over_budget(self) -> None:
        """Test that Explorer flags when over token budget."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": f"f{i}.py", "relevance": "LOW"} for i in range(100)],
                "dependencies": [],
                "context_summary": "Too many files",
                "token_estimate": 15000,  # Over 10K budget
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find all", session_id="test", context={"max_files": 100})

        response = await explorer.execute(task)

        assert response.success is True
        assert response.metadata["within_budget"] is False  # Over budget

    @pytest.mark.asyncio
    async def test_explorer_stays_within_budget(self) -> None:
        """Test that Explorer stays within token budget."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": "file1.py", "relevance": "HIGH"},
                    {"path": "file2.py", "relevance": "HIGH"},
                ],
                "dependencies": [],
                "context_summary": "2 focused files",
                "token_estimate": 3000,  # Well under 10K
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find specific files", session_id="test")

        response = await explorer.execute(task)

        assert response.success is True
        assert response.metadata["within_budget"] is True  # Within budget


class TestExplorerPromptBuilding:
    """Test Explorer prompt construction."""

    def test_build_search_prompt_basic(self) -> None:
        """Test basic search prompt construction."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        task = AgentTask(request="Find database models", session_id="test")

        prompt = explorer._build_search_prompt(task, max_files=10)

        assert "Find database models" in prompt
        assert "Maximum 10 files" in prompt
        assert "REQUEST:" in prompt

    def test_build_search_prompt_with_constraints(self) -> None:
        """Test prompt includes context constraints."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Find API routes",
            session_id="test",
            context={
                "project_root": "/app",
                "file_patterns": "*.py",
            },
        )

        prompt = explorer._build_search_prompt(task, max_files=5)

        assert "/app" in prompt
        assert "*.py" in prompt


class TestExplorerFallbackExtraction:
    """Test fallback file extraction from text."""

    def test_extract_python_files(self) -> None:
        """Test extracting Python file paths from text."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())

        text = """
        The relevant files are:
        - src/auth/jwt.py contains token logic
        - src/api/routes.py has the endpoints
        - tests/test_auth.py for testing
        """

        result = explorer._extract_files_fallback(text)

        assert len(result["relevant_files"]) >= 3
        paths = [f["path"] for f in result["relevant_files"]]
        assert any("jwt.py" in p for p in paths)
        assert any("routes.py" in p for p in paths)

    def test_extract_mixed_file_types(self) -> None:
        """Test extracting various code file types."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())

        text = "Files: app.js, utils.ts, main.go, test.java"

        result = explorer._extract_files_fallback(text)

        # Should extract code files only
        assert len(result["relevant_files"]) >= 3
        assert result["context_summary"] == "Files extracted from text response (fallback)"

    def test_extract_limits_to_10_files(self) -> None:
        """Test that fallback extraction limits to 10 files."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())

        # Create text with 20 file mentions
        text = " ".join([f"file{i}.py" for i in range(20)])

        result = explorer._extract_files_fallback(text)

        assert len(result["relevant_files"]) <= 10  # Max 10


class TestExplorerErrorHandling:
    """Test Explorer error handling."""

    @pytest.mark.asyncio
    async def test_explorer_handles_llm_failure(self) -> None:
        """Test that Explorer handles LLM failures gracefully."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(side_effect=Exception("LLM error"))

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)

        assert response.success is False
        assert "failed" in response.reasoning.lower()
        assert "LLM error" in response.error

    @pytest.mark.asyncio
    async def test_explorer_handles_invalid_json(self) -> None:
        """Test Explorer handles non-JSON responses."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value="The files are: src/main.py and src/utils.py"
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)

        # Should fall back to text extraction
        assert response.success is True
        assert len(response.data["relevant_files"]) >= 1

    @pytest.mark.asyncio
    async def test_explorer_handles_missing_files_field(self) -> None:
        """Test handling of malformed LLM response."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                # Missing "relevant_files" field
                "context_summary": "Some summary",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)

        assert response.success is False
        assert "missing 'relevant_files'" in response.reasoning.lower()
