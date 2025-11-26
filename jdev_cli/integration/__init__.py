"""Integration module - connects parser, LLM, and shell execution.

This module implements Phase 2.1 of the master plan:
- Parser → Shell Bridge
- Safety validation
- Session management
- End-to-end tool execution

Best practices from:
- Cursor AI: Semantic understanding + RAG
- Claude Code: Hook system + safety
- GitHub Codex: Tool calling + sandboxing
- Aider AI: Context mapping + function calling
"""

from .safety import SafetyValidator, safety_validator
from .session import Session, SessionManager, session_manager
from .shell_bridge import ShellBridge, ToolExecutionResult, shell_bridge

__all__ = [
    # Safety
    "SafetyValidator",
    "safety_validator",

    # Session
    "Session",
    "SessionManager",
    "session_manager",

    # Shell Bridge
    "ShellBridge",
    "ToolExecutionResult",
    "shell_bridge",
]
