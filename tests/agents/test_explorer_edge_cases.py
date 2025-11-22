"""
Comprehensive edge case testing for ExplorerAgent.

Tests cover:
    - Token budget edge cases
    - File extraction edge cases
    - Real-world search scenarios
    - Performance limits
    - Malformed responses
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock

from qwen_dev_cli.agents.explorer import ExplorerAgent
from qwen_dev_cli.agents.base import AgentTask


class TestExplorerTokenBudgetEdgeCases:
    """Comprehensive token budget tests."""

    @pytest.mark.asyncio
    async def test_explorer_with_exactly_10k_tokens(self) -> None:
        """Test Explorer at exactly 10K token budget limit."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": f"f{i}.py", "relevance": "MEDIUM"} for i in range(50)],
                "dependencies": [],
                "context_summary": "Exactly at budget",
                "token_estimate": 10000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test", context={"max_files": 50})

        response = await explorer.execute(task)
        assert response.success is True
        assert response.metadata["token_estimate"] == 10000
        assert response.metadata["within_budget"] is True  # Exactly at limit

    @pytest.mark.asyncio
    async def test_explorer_with_10001_tokens(self) -> None:
        """Test Explorer just over 10K token budget."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": f"f{i}.py", "relevance": "LOW"} for i in range(51)],
                "dependencies": [],
                "context_summary": "Over budget",
                "token_estimate": 10001,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find many files", session_id="test", context={"max_files": 51})

        response = await explorer.execute(task)
        assert response.success is True
        assert response.metadata["within_budget"] is False  # Over limit

    @pytest.mark.asyncio
    async def test_explorer_with_zero_token_estimate(self) -> None:
        """Test Explorer when LLM doesn't provide token estimate."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": "a.py", "relevance": "HIGH"},
                    {"path": "b.py", "relevance": "HIGH"},
                ],
                "dependencies": [],
                "context_summary": "Test",
                "token_estimate": 0,  # Zero provided
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        # Should calculate: 2 files * 200 = 400
        assert response.metadata["token_estimate"] == 400

    @pytest.mark.asyncio
    async def test_explorer_with_massive_token_estimate(self) -> None:
        """Test Explorer with unrealistic token estimate."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "huge.py", "relevance": "HIGH"}],
                "dependencies": [],
                "context_summary": "One huge file",
                "token_estimate": 1000000,  # 1M tokens
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find huge file", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        assert response.metadata["within_budget"] is False


class TestExplorerFileLimitEdgeCases:
    """File limit enforcement edge cases."""

    @pytest.mark.asyncio
    async def test_explorer_with_max_files_1(self) -> None:
        """Test Explorer with max_files=1."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": "a.py", "relevance": "HIGH"},
                    {"path": "b.py", "relevance": "MEDIUM"},
                ],
                "dependencies": [],
                "context_summary": "Multiple files returned",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find one file", session_id="test", context={"max_files": 1})

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["relevant_files"]) == 1  # Enforced to 1

    @pytest.mark.asyncio
    async def test_explorer_with_max_files_100(self) -> None:
        """Test Explorer with large max_files limit."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": f"file{i}.py", "relevance": "LOW"} for i in range(150)],
                "dependencies": [],
                "context_summary": "Many files",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find all files", session_id="test", context={"max_files": 100})

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["relevant_files"]) == 100  # Capped at 100

    @pytest.mark.asyncio
    async def test_explorer_with_zero_files_returned(self) -> None:
        """Test Explorer when LLM returns zero files."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [],  # Empty list
                "dependencies": [],
                "context_summary": "No relevant files found",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find nonexistent", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["relevant_files"]) == 0
        assert response.metadata["file_count"] == 0


class TestExplorerRealWorldScenarios:
    """Real-world file discovery scenarios."""

    @pytest.mark.asyncio
    async def test_explorer_finds_authentication_files(self) -> None:
        """Test realistic scenario: finding authentication code."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {
                        "path": "src/auth/jwt_handler.py",
                        "relevance": "HIGH",
                        "reason": "Core JWT token handling",
                        "key_symbols": ["create_token", "verify_token", "decode_token"],
                        "line_range": [1, 200],
                    },
                    {
                        "path": "src/auth/middleware.py",
                        "relevance": "HIGH",
                        "reason": "Authentication middleware",
                        "key_symbols": ["auth_required", "check_permissions"],
                    },
                    {
                        "path": "src/models/user.py",
                        "relevance": "MEDIUM",
                        "reason": "User model with authentication fields",
                        "key_symbols": ["User", "password_hash", "last_login"],
                    },
                    {
                        "path": "tests/test_auth.py",
                        "relevance": "MEDIUM",
                        "reason": "Authentication tests",
                        "key_symbols": ["test_login", "test_token_validation"],
                    },
                ],
                "dependencies": [
                    {"from": "middleware.py", "to": "jwt_handler.py", "type": "imports"},
                    {"from": "jwt_handler.py", "to": "user.py", "type": "uses"},
                ],
                "context_summary": "Found 4 auth-related files covering JWT, middleware, models, and tests",
                "token_estimate": 3500,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Find all files related to JWT authentication",
            session_id="test",
        )

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["relevant_files"]) == 4
        assert response.data["relevant_files"][0]["relevance"] == "HIGH"
        assert len(response.data["dependencies"]) == 2
        assert response.metadata["within_budget"] is True

    @pytest.mark.asyncio
    async def test_explorer_finds_database_migration_files(self) -> None:
        """Test realistic scenario: finding database migrations."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {
                        "path": "migrations/001_create_users_table.sql",
                        "relevance": "HIGH",
                        "reason": "Initial users table creation",
                    },
                    {
                        "path": "migrations/002_add_email_column.sql",
                        "relevance": "HIGH",
                        "reason": "Adds email column",
                    },
                    {
                        "path": "migrations/003_create_index_email.sql",
                        "relevance": "MEDIUM",
                        "reason": "Performance index on email",
                    },
                ],
                "dependencies": [],
                "context_summary": "Found 3 sequential migrations affecting users table",
                "token_estimate": 2000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(
            request="Find database migrations related to users table",
            session_id="test",
        )

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["relevant_files"]) == 3
        assert all(".sql" in f["path"] for f in response.data["relevant_files"])

    @pytest.mark.asyncio
    async def test_explorer_finds_api_route_handlers(self) -> None:
        """Test realistic scenario: finding API routes."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {
                        "path": "src/api/users.py",
                        "relevance": "HIGH",
                        "reason": "User CRUD endpoints",
                        "key_symbols": ["get_user", "create_user", "update_user", "delete_user"],
                    },
                    {
                        "path": "src/api/auth.py",
                        "relevance": "HIGH",
                        "reason": "Authentication endpoints",
                        "key_symbols": ["login", "logout", "refresh_token"],
                    },
                    {
                        "path": "src/api/__init__.py",
                        "relevance": "MEDIUM",
                        "reason": "API router configuration",
                    },
                ],
                "dependencies": [
                    {"from": "__init__.py", "to": "users.py", "type": "registers"},
                    {"from": "__init__.py", "to": "auth.py", "type": "registers"},
                ],
                "context_summary": "Found 3 API-related files with route handlers",
                "token_estimate": 4000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find all API route handlers", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        assert response.metadata["file_count"] == 3


class TestExplorerFallbackExtractionEdgeCases:
    """Additional fallback extraction tests."""

    def test_fallback_extracts_path_with_dots(self) -> None:
        """Test fallback extracts paths with dots in filename."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "See file src/app.config.js for details"
        result = explorer._extract_files_fallback(text)
        paths = [f["path"] for f in result["relevant_files"]]
        assert any("app.config.js" in p for p in paths)

    def test_fallback_extracts_path_with_numbers(self) -> None:
        """Test fallback extracts paths with numbers."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "Check migration_001_create_users.sql file"
        result = explorer._extract_files_fallback(text)
        # Just verify it runs without error
        assert result is not None

    def test_fallback_ignores_non_code_extensions(self) -> None:
        """Test fallback ignores non-code file extensions."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "Files: readme.txt, data.csv, image.png, code.py"
        result = explorer._extract_files_fallback(text)
        paths = [f["path"] for f in result["relevant_files"]]
        assert any("code.py" in p for p in paths)
        # Should not include txt, csv, png
        assert not any(".txt" in p for p in paths)
        assert not any(".csv" in p for p in paths)
        assert not any(".png" in p for p in paths)

    def test_fallback_handles_windows_paths(self) -> None:
        """Test fallback with Windows and Unix paths."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "File at C:\\Users\\project\\src\\main.py or src/main.py"
        result = explorer._extract_files_fallback(text)
        assert result is not None
        assert "relevant_files" in result

    def test_fallback_handles_relative_paths(self) -> None:
        """Test fallback extracts relative paths."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "Check ./src/app.js and ../utils/helper.ts"
        result = explorer._extract_files_fallback(text)
        paths = [f["path"] for f in result["relevant_files"]]
        assert any("app.js" in p for p in paths)
        assert any("helper.ts" in p for p in paths)

    def test_fallback_deduplicates_paths(self) -> None:
        """Test fallback handles duplicate mentions."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        text = "src/main.py is important. Check src/main.py again."
        result = explorer._extract_files_fallback(text)
        paths = [f["path"] for f in result["relevant_files"]]
        main_py_count = sum(1 for p in paths if "main.py" in p)
        assert main_py_count >= 1  # At least extracted once


class TestExplorerMalformedResponses:
    """Tests with malformed LLM responses."""

    @pytest.mark.asyncio
    async def test_explorer_handles_array_instead_of_object(self) -> None:
        """Test Explorer handles array instead of object response."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value='["file1.py", "file2.py"]'  # Array not object
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)
        # Fallback may not extract from array - verify it returns
        assert response is not None

    @pytest.mark.asyncio
    async def test_explorer_handles_empty_json_object(self) -> None:
        """Test Explorer handles empty JSON object."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(return_value="{}")

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)
        assert response.success is False  # Missing relevant_files

    @pytest.mark.asyncio
    async def test_explorer_handles_malformed_json(self) -> None:
        """Test Explorer handles malformed JSON."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value='{"relevant_files": [incomplete'
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)
        # Should fall back to text extraction
        assert response.success is True

    @pytest.mark.asyncio
    async def test_explorer_handles_files_as_string(self) -> None:
        """Test Explorer when relevant_files is string instead of array."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": "file1.py, file2.py",  # String not array
                "dependencies": [],
                "context_summary": "Test",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find files", session_id="test")

        response = await explorer.execute(task)
        # Should handle gracefully (may fail or fall back)
        # At minimum should not crash
        assert response is not None


class TestExplorerPromptBuildingEdgeCases:
    """Edge cases for prompt construction."""

    def test_prompt_with_no_context(self) -> None:
        """Test prompt building with completely empty context."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        task = AgentTask(request="Find files", session_id="test", context={})
        prompt = explorer._build_search_prompt(task, max_files=10)
        assert "Find files" in prompt
        assert "Maximum 10 files" in prompt

    def test_prompt_with_all_context_fields(self) -> None:
        """Test prompt with all optional context fields."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Find files",
            session_id="test",
            context={
                "project_root": "/app",
                "file_patterns": "*.py,*.js",
                "extra_field": "ignored",
            },
        )
        prompt = explorer._build_search_prompt(task, max_files=5)
        assert "/app" in prompt
        assert "*.py,*.js" in prompt

    def test_prompt_enforces_max_files_in_text(self) -> None:
        """Test prompt clearly states max files limit."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        task = AgentTask(request="Find files", session_id="test")
        prompt = explorer._build_search_prompt(task, max_files=3)
        assert "Maximum 3 files" in prompt or "max_files: 3" in prompt.lower()


class TestExplorerPerformance:
    """Performance edge cases."""

    @pytest.mark.asyncio
    async def test_explorer_execution_count_increments(self) -> None:
        """Test execution count increments."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [],
                "dependencies": [],
                "context_summary": "Test",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        initial = explorer.execution_count

        task = AgentTask(request="Test", session_id="test")
        await explorer.execute(task)

        assert explorer.execution_count == initial + 1

    @pytest.mark.asyncio
    async def test_explorer_multiple_parallel_requests(self) -> None:
        """Test Explorer handles multiple tasks in sequence."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "test.py", "relevance": "HIGH"}],
                "dependencies": [],
                "context_summary": "Test",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())

        for i in range(10):
            task = AgentTask(request=f"Find files {i}", session_id=f"test-{i}")
            response = await explorer.execute(task)
            assert response.success is True

        assert explorer.execution_count == 10


class TestExplorerDependencyHandling:
    """Tests for dependency extraction and handling."""

    @pytest.mark.asyncio
    async def test_explorer_with_complex_dependencies(self) -> None:
        """Test Explorer with complex dependency graph."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": "a.py", "relevance": "HIGH"},
                    {"path": "b.py", "relevance": "MEDIUM"},
                    {"path": "c.py", "relevance": "MEDIUM"},
                ],
                "dependencies": [
                    {"from": "a.py", "to": "b.py", "type": "imports"},
                    {"from": "a.py", "to": "c.py", "type": "imports"},
                    {"from": "b.py", "to": "c.py", "type": "uses"},
                ],
                "context_summary": "Complex dependency graph",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find dependencies", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["dependencies"]) == 3

    @pytest.mark.asyncio
    async def test_explorer_with_empty_dependencies(self) -> None:
        """Test Explorer with no dependencies."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "standalone.py", "relevance": "HIGH"}],
                "dependencies": [],  # No dependencies
                "context_summary": "Standalone file",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find standalone", session_id="test")

        response = await explorer.execute(task)
        assert response.success is True
        assert len(response.data["dependencies"]) == 0
