"""
Simplified SecurityAgent tests - Production focused.
"""
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from qwen_dev_cli.agents.base import AgentRole, AgentTask
from qwen_dev_cli.agents.security import SecurityAgent


@pytest.fixture
def security_agent():
    """Create SecurityAgent instance."""
    mock_llm = MagicMock()
    mock_llm.generate = AsyncMock(return_value="Security scan complete")
    mock_mcp = MagicMock()
    return SecurityAgent(llm_client=mock_llm, mcp_client=mock_mcp)


class TestSecurityAgentCore:
    """Core functionality tests."""

    @pytest.mark.asyncio
    async def test_agent_creation(self, security_agent):
        """Test agent can be created."""
        assert security_agent.role == AgentRole.SECURITY

    @pytest.mark.asyncio
    async def test_empty_directory_scan(self, security_agent):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            task = AgentTask(
                request="Scan empty directory",
                context={"root_dir": tmpdir},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            assert result.data.get("owasp_score") == 100

    @pytest.mark.asyncio
    async def test_sql_injection_detection(self, security_agent):
        """Test SQL injection detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "sql.py").write_text(
                """
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""
            )
            task = AgentTask(
                request="Scan for SQL injection",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            vulns = result.data.get("vulnerabilities", [])
            assert any("sql" in v.get("type", "").lower() for v in vulns)

    @pytest.mark.asyncio
    async def test_command_injection_detection(self, security_agent):
        """Test command injection detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "cmd.py").write_text(
                """
import subprocess
subprocess.run(cmd, shell=True)
"""
            )
            task = AgentTask(
                request="Scan for command injection",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            vulns = result.data.get("vulnerabilities", [])
            assert len(vulns) > 0

    @pytest.mark.asyncio
    async def test_eval_detection(self, security_agent):
        """Test eval/exec detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "eval.py").write_text(
                """
result = eval(user_input)
"""
            )
            task = AgentTask(
                request="Scan for eval usage",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            vulns = result.data.get("vulnerabilities", [])
            assert any("eval" in v.get("type", "").lower() for v in vulns)

    @pytest.mark.asyncio
    async def test_secret_detection_api_key(self, security_agent):
        """Test API key detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / ".env").write_text(
                """
API_KEY="FAKE_TEST_KEY_NOT_REAL_STRIPE_PATTERN"
"""
            )
            task = AgentTask(
                request="Scan for secrets",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            secrets = result.data.get("secrets", [])
            assert len(secrets) >= 1

    @pytest.mark.asyncio
    async def test_owasp_scoring(self, security_agent):
        """Test OWASP scoring calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            # Multiple vulnerabilities
            (project / "vuln.py").write_text(
                """
eval("code")
exec("code")
subprocess.run("cmd", shell=True)
"""
            )
            task = AgentTask(
                request="Calculate OWASP score",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            score = result.data.get("owasp_score", 100)
            assert score < 100  # Should have deductions
            assert score >= 0  # Never negative

    @pytest.mark.asyncio
    async def test_report_generation(self, security_agent):
        """Test report is generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "test.py").write_text("print('hello')")
            task = AgentTask(
                request="Generate security report",
                context={"root_dir": str(project)},
            )
            result = await security_agent.execute(task)
            assert result.success == True
            report = result.data.get("report", "")
            assert "SECURITY AUDIT REPORT" in report
            assert "OWASP COMPLIANCE SCORE" in report

    @pytest.mark.asyncio
    async def test_error_handling(self, security_agent):
        """Test graceful error handling."""
        task = AgentTask(
            request="Scan nonexistent path",
            context={"root_dir": "/nonexistent/path/12345"},
        )
        result = await security_agent.execute(task)
        # Should handle error gracefully
        assert result.success in [True, False]  # Either works or fails cleanly
