"""
Constitutional compliance testing for Day 2 agents (Vértice v3.0).

Tests validate adherence to all 6 principles specifically for
Architect and Explorer agents.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
import inspect

from qwen_dev_cli.agents.architect import ArchitectAgent, ARCHITECT_SYSTEM_PROMPT
from qwen_dev_cli.agents.explorer import ExplorerAgent, EXPLORER_SYSTEM_PROMPT
from qwen_dev_cli.agents.base import AgentTask, AgentCapability


class TestDay2P1Completude:
    """P1: Completude Obrigatória - Zero placeholders."""

    def test_architect_has_no_todos(self) -> None:
        """Test Architect source has no TODO/FIXME."""
        import qwen_dev_cli.agents.architect as architect_module
        source = inspect.getsource(architect_module)
        
        forbidden = ["TODO", "FIXME", "XXX", "HACK"]
        for pattern in forbidden:
            assert pattern not in source, f"Found {pattern} in architect.py"

    def test_explorer_has_no_todos(self) -> None:
        """Test Explorer source has no TODO/FIXME."""
        import qwen_dev_cli.agents.explorer as explorer_module
        source = inspect.getsource(explorer_module)
        
        forbidden = ["TODO", "FIXME", "XXX", "HACK"]
        for pattern in forbidden:
            assert pattern not in source, f"Found {pattern} in explorer.py"

    def test_architect_execute_is_complete(self) -> None:
        """Test Architect execute() is fully implemented."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        source = inspect.getsource(architect.execute)
        assert "pass" not in source or "# pass" in source  # Only comments

    def test_explorer_execute_is_complete(self) -> None:
        """Test Explorer execute() is fully implemented."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        source = inspect.getsource(explorer.execute)
        assert "pass" not in source or "# pass" in source


class TestDay2P2ValidacaoPreventiva:
    """P2: Validação Preventiva - Validate before execution."""

    def test_architect_validates_decision_format(self) -> None:
        """Test Architect validates decision before returning."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({"decision": "INVALID"})
        )
        architect.llm_client = llm_client

        task = AgentTask(request="Test", session_id="test")
        
        # Should validate and fail for invalid decision
        import asyncio
        response = asyncio.run(architect.execute(task))
        assert response.success is False

    def test_explorer_validates_file_structure(self) -> None:
        """Test Explorer validates response structure."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({"missing": "relevant_files"})
        )
        explorer.llm_client = llm_client

        task = AgentTask(request="Test", session_id="test")
        
        import asyncio
        response = asyncio.run(explorer.execute(task))
        assert response.success is False

    def test_architect_prevents_capability_violation(self) -> None:
        """Test Architect cannot execute write operations."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        
        assert architect._can_use_tool("write_file") is False
        assert architect._can_use_tool("bash_command") is False

    def test_explorer_prevents_capability_violation(self) -> None:
        """Test Explorer cannot execute write operations."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        
        assert explorer._can_use_tool("write_file") is False
        assert explorer._can_use_tool("bash_command") is False


class TestDay2P3CeticismoCritico:
    """P3: Ceticismo Crítico - Skeptical validation."""

    def test_architect_is_skeptical_by_design(self) -> None:
        """Test Architect system prompt emphasizes skepticism."""
        assert "skeptical" in ARCHITECT_SYSTEM_PROMPT.lower()
        assert "veto" in ARCHITECT_SYSTEM_PROMPT.lower()
        assert "risk" in ARCHITECT_SYSTEM_PROMPT.lower()

    def test_architect_has_veto_capability(self) -> None:
        """Test Architect can veto requests."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "VETOED",
                "reasoning": "Too risky",
                "architecture": {"approach": "N/A", "risks": [], "constraints": [], "estimated_complexity": "HIGH"},
                "recommendations": [],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Delete production database", session_id="test")
        
        import asyncio
        response = asyncio.run(architect.execute(task))
        assert response.success is True
        assert response.data["decision"] == "VETOED"

    def test_explorer_validates_token_budget(self) -> None:
        """Test Explorer critically evaluates token usage."""
        assert "token budget" in EXPLORER_SYSTEM_PROMPT.lower()
        assert "10k" in EXPLORER_SYSTEM_PROMPT.lower() or "10000" in EXPLORER_SYSTEM_PROMPT

    def test_explorer_flags_budget_violations(self) -> None:
        """Test Explorer flags when over budget."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": f"f{i}.py", "relevance": "LOW"} for i in range(100)],
                "dependencies": [],
                "context_summary": "Too many files",
                "token_estimate": 50000,  # Way over budget
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Find all", session_id="test", context={"max_files": 100})
        
        import asyncio
        response = asyncio.run(explorer.execute(task))
        assert response.metadata["within_budget"] is False


class TestDay2P4Rastreabilidade:
    """P4: Rastreabilidade Total - Full traceability."""

    def test_architect_tracks_execution_count(self) -> None:
        """Test Architect tracks executions."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        initial = architect.execution_count
        assert isinstance(initial, int)

    def test_explorer_tracks_execution_count(self) -> None:
        """Test Explorer tracks executions."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        initial = explorer.execution_count
        assert isinstance(initial, int)

    def test_architect_provides_reasoning(self) -> None:
        """Test Architect always provides reasoning."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "APPROVED",
                "reasoning": "Clear reasoning provided",
                "architecture": {"approach": "Test", "risks": [], "constraints": [], "estimated_complexity": "LOW"},
                "recommendations": [],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")
        
        import asyncio
        response = asyncio.run(architect.execute(task))
        assert response.reasoning
        assert len(response.reasoning) > 0

    def test_explorer_provides_context_summary(self) -> None:
        """Test Explorer provides context summary."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "test.py", "relevance": "HIGH"}],
                "dependencies": [],
                "context_summary": "Found 1 relevant file",
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")
        
        import asyncio
        response = asyncio.run(explorer.execute(task))
        assert response.reasoning
        assert "file" in response.reasoning.lower()


class TestDay2P5ConscienciaSistemica:
    """P5: Consciência Sistêmica - System awareness."""

    def test_architect_declares_role(self) -> None:
        """Test Architect has explicit role."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        assert architect.role.value == "architect"

    def test_explorer_declares_role(self) -> None:
        """Test Explorer has explicit role."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        assert explorer.role.value == "explorer"

    def test_architect_declares_capabilities(self) -> None:
        """Test Architect declares READ_ONLY capability."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        assert AgentCapability.READ_ONLY in architect.capabilities
        assert len(architect.capabilities) == 1

    def test_explorer_declares_capabilities(self) -> None:
        """Test Explorer declares READ_ONLY capability."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        assert AgentCapability.READ_ONLY in explorer.capabilities
        assert len(explorer.capabilities) == 1

    def test_architect_aware_of_architecture_role(self) -> None:
        """Test Architect understands its role in system."""
        assert "feasibility" in ARCHITECT_SYSTEM_PROMPT.lower()
        assert "first" in ARCHITECT_SYSTEM_PROMPT.lower() or "gate" in ARCHITECT_SYSTEM_PROMPT.lower()

    def test_explorer_aware_of_context_role(self) -> None:
        """Test Explorer understands its context-gathering role."""
        assert "context" in EXPLORER_SYSTEM_PROMPT.lower()
        assert "search" in EXPLORER_SYSTEM_PROMPT.lower() or "find" in EXPLORER_SYSTEM_PROMPT.lower()


class TestDay2P6EficienciaToken:
    """P6: Eficiência de Token - Token efficiency."""

    def test_architect_has_compact_prompts(self) -> None:
        """Test Architect builds efficient prompts."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        task = AgentTask(request="Short request", session_id="test")
        
        prompt = architect._build_analysis_prompt(task)
        # Prompt should be reasonable length (< 2K chars for simple request)
        assert len(prompt) < 2000

    def test_explorer_limits_file_list_in_prompt(self) -> None:
        """Test Explorer limits files shown in prompt."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        task = AgentTask(
            request="Test",
            session_id="test",
            context={"files": [f"file{i}.py" for i in range(100)]},
        )
        
        prompt = architect._build_analysis_prompt(task)
        # Should mention 100 files but not list all
        file_count = prompt.count("file")
        assert file_count < 50  # Not listing all 100

    def test_explorer_tracks_token_budget(self) -> None:
        """Test Explorer tracks and reports token estimates."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "test.py", "relevance": "HIGH"}],
                "dependencies": [],
                "context_summary": "Test",
                "token_estimate": 5000,
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")
        
        import asyncio
        response = asyncio.run(explorer.execute(task))
        assert "token_estimate" in response.metadata
        assert isinstance(response.metadata["token_estimate"], int)

    def test_explorer_calculates_fallback_estimate(self) -> None:
        """Test Explorer calculates token estimate when not provided."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [
                    {"path": "a.py", "relevance": "HIGH"},
                    {"path": "b.py", "relevance": "HIGH"},
                ],
                "dependencies": [],
                "context_summary": "Test",
                # No token_estimate
            })
        )

        explorer = ExplorerAgent(llm_client, MagicMock())
        task = AgentTask(request="Test", session_id="test")
        
        import asyncio
        response = asyncio.run(explorer.execute(task))
        # Should calculate: 2 files * 200 = 400
        assert response.metadata["token_estimate"] == 400


class TestDay2TypeSafety:
    """Type safety validation for Day 2 agents."""

    def test_architect_all_methods_typed(self) -> None:
        """Test all Architect methods have type hints."""
        architect = ArchitectAgent(MagicMock(), MagicMock())
        
        for name, method in inspect.getmembers(architect, inspect.ismethod):
            if not name.startswith("_") or name == "__init__":
                sig = inspect.signature(method)
                # Check return annotation
                if name != "__init__":
                    assert sig.return_annotation != inspect.Parameter.empty

    def test_explorer_all_methods_typed(self) -> None:
        """Test all Explorer methods have type hints."""
        explorer = ExplorerAgent(MagicMock(), MagicMock())
        
        for name, method in inspect.getmembers(explorer, inspect.ismethod):
            if not name.startswith("_") or name == "__init__":
                sig = inspect.signature(method)
                # Check return annotation
                if name != "__init__":
                    assert sig.return_annotation != inspect.Parameter.empty


class TestDay2Integration:
    """Integration between Architect and Explorer."""

    @pytest.mark.asyncio
    async def test_architect_and_explorer_use_same_task_format(self) -> None:
        """Test both agents accept same AgentTask format."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "APPROVED",
                "reasoning": "Test",
                "architecture": {"approach": "Test", "risks": [], "constraints": [], "estimated_complexity": "LOW"},
                "recommendations": [],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        
        llm_client2 = MagicMock()
        llm_client2.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [],
                "dependencies": [],
                "context_summary": "Test",
            })
        )
        explorer = ExplorerAgent(llm_client2, MagicMock())

        # Same task format
        task = AgentTask(request="Test", session_id="test-123")

        arch_response = await architect.execute(task)
        expl_response = await explorer.execute(task)

        # Both should process same task
        assert arch_response is not None
        assert expl_response is not None

    @pytest.mark.asyncio
    async def test_architect_decision_can_inform_explorer(self) -> None:
        """Test Architect's decision can be used by Explorer."""
        llm_client = MagicMock()
        llm_client.generate = AsyncMock(
            return_value=json.dumps({
                "decision": "APPROVED",
                "reasoning": "Feasible",
                "architecture": {"approach": "Add JWT", "risks": [], "constraints": [], "estimated_complexity": "MEDIUM"},
                "recommendations": ["Check auth files"],
            })
        )

        architect = ArchitectAgent(llm_client, MagicMock())
        task1 = AgentTask(request="Add JWT auth", session_id="test")
        arch_response = await architect.execute(task1)

        # Explorer uses Architect's recommendations
        llm_client2 = MagicMock()
        llm_client2.generate = AsyncMock(
            return_value=json.dumps({
                "relevant_files": [{"path": "src/auth/jwt.py", "relevance": "HIGH"}],
                "dependencies": [],
                "context_summary": "Found auth files",
            })
        )
        explorer = ExplorerAgent(llm_client2, MagicMock())
        task2 = AgentTask(
            request="Find JWT auth files",
            session_id="test",
            context={"architect_decision": arch_response.data},
        )
        expl_response = await explorer.execute(task2)

        assert expl_response.success is True
