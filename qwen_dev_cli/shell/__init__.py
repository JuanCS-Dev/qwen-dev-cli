"""
shell: Interactive Shell Package.

This package provides the interactive shell interface for qwen-dev-cli.

Modules:
- context: Session context management (SessionContext)
- safety: Command safety evaluation
- tool_executor: Tool execution with recovery
- executor: ShellExecutor for LLM-driven tool execution
- streaming_integration: Streaming response handling
- repl: REPL entry point

Usage:
    from qwen_dev_cli.shell import InteractiveShell, SessionContext
    from qwen_dev_cli.shell.safety import get_safety_level, is_dangerous
    from qwen_dev_cli.shell.tool_executor import ToolExecutor
"""

from .repl import main
from .context import SessionContext

# Re-export from shell_main for backward compatibility
# InteractiveShell is still in shell_main.py (gradual migration)
from qwen_dev_cli.shell_main import InteractiveShell

# Export safety utilities
from .safety import (
    get_safety_level,
    is_safe,
    is_dangerous,
    needs_confirmation,
    SAFE_COMMANDS,
    DANGEROUS_COMMANDS,
)

# Export tool executor
from .tool_executor import ToolExecutor, ExecutionAttempt

__all__ = [
    # Main classes
    "main",
    "InteractiveShell",
    "SessionContext",
    # Tool execution
    "ToolExecutor",
    "ExecutionAttempt",
    # Safety
    "get_safety_level",
    "is_safe",
    "is_dangerous",
    "needs_confirmation",
    "SAFE_COMMANDS",
    "DANGEROUS_COMMANDS",
]
