"""
Command Handlers Module - SCALE & SUSTAIN Phase 1.2.

Extracted from shell_main.py to reduce cyclomatic complexity.

Components:
- CommandDispatcher: Routes commands to handlers
- LSPHandler: All LSP-related commands
- BasicHandler: Basic system commands (/help, /exit, etc.)
- HistoryHandler: History and session commands
- WorkflowHandler: Workflow and squad commands
- IndexHandler: Indexing and search commands
- RefactorHandler: Refactoring commands
- InputHandler: User input processing (Phase 1.2.4)

Author: JuanCS Dev
Date: 2025-11-26
"""

from .dispatcher import CommandDispatcher, CommandResult
from .lsp_handler import LSPHandler
from .basic_handler import BasicHandler
from .history_handler import HistoryHandler
from .workflow_handler import WorkflowHandler
from .index_handler import IndexHandler
from .refactor_handler import RefactorHandler
from .input_handler import (
    InputHandler,
    InputType,
    ParsedInput,
    ValidationResult,
    ValidationStatus,
)

__all__ = [
    'CommandDispatcher',
    'CommandResult',
    'LSPHandler',
    'BasicHandler',
    'HistoryHandler',
    'WorkflowHandler',
    'IndexHandler',
    'RefactorHandler',
    'InputHandler',
    'InputType',
    'ParsedInput',
    'ValidationResult',
    'ValidationStatus',
]
