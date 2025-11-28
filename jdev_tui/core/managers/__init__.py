"""
Managers Module - Extracted Bridge Responsibilities.

Part of SCALE & SUSTAIN Phase 1.1 - Bridge Refactoring.

This module contains specialized managers extracted from the Bridge class
to reduce its complexity from 74 methods to ~52 methods.

Managers:
- TodoManager: TODO list management
- StatusManager: System health and permissions
- PullRequestManager: GitHub PR operations
- MemoryManager: Persistent memory (MEMORY.md)
- ContextManager: Conversation context management
- AuthenticationManager: API key management

Author: JuanCS Dev
Date: 2025-11-26
"""

from .todo_manager import TodoManager
from .status_manager import StatusManager
from .pr_manager import PullRequestManager
from .memory_manager import MemoryManager
from .context_manager import ContextManager
from .auth_manager import AuthenticationManager

__all__ = [
    'TodoManager',
    'StatusManager',
    'PullRequestManager',
    'MemoryManager',
    'ContextManager',
    'AuthenticationManager',
]
