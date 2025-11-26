"""Tool implementations.

This module provides all tools for the Juan-Dev-Code CLI.

Tool Categories:
- File Operations: ReadFileTool, WriteFileTool, EditFileTool, etc.
- Search: SearchFilesTool, GlobTool, GrepTool
- Execution: BashCommandTool, BackgroundTaskTool
- Git: GitStatusTool, GitDiffTool
- Context: GetContextTool, MemoryReadTool, MemoryWriteTool
- Planning: EnterPlanModeTool, ExitPlanModeTool
- User Interaction: AskUserQuestionTool
- Web: WebFetchTool, WebSearchTool
- Notebooks: NotebookReadTool, NotebookEditTool
- Subagents: TaskTool

Claude Code Parity:
- Memory system (CLAUDE.md/MEMORY.md)
- AskUserQuestion for user interaction
- Edit replace_all for bulk replacements
- NotebookEdit for Jupyter notebooks
- EnterPlanMode/ExitPlanMode for structured planning
- Task tool with resume capability
"""

# Base classes
from .base import Tool, ToolCategory, ToolResult, ToolRegistry

# File operations
from .file_ops import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListDirectoryTool,
    DeleteFileTool,
)

# File management
from .file_mgmt import (
    MoveFileTool,
    CopyFileTool,
    CreateDirectoryTool,
    ReadMultipleFilesTool,
    InsertLinesTool,
)

# Search tools
from .search import SearchFilesTool, GetDirectoryTreeTool

# Claude Code parity tools
from .claude_parity_tools import (
    GlobTool,
    LSTool,
    MultiEditTool,
    WebFetchTool,
    WebSearchTool,
    TodoReadTool,
    TodoWriteTool,
    NotebookReadTool,
    NotebookEditTool,
    BackgroundTaskTool,
    TaskTool,
    AskUserQuestionTool,
    get_claude_parity_tools,
)

# Plan mode tools
from .plan_mode import (
    EnterPlanModeTool,
    ExitPlanModeTool,
    AddPlanNoteTool,
    GetPlanStatusTool,
    get_plan_mode_tools,
    get_plan_state,
    reset_plan_state,
)

# Execution tools
from .exec_hardened import BashCommandTool

# Git tools
from .git_ops import GitStatusTool, GitDiffTool

# Context tools
from .context import GetContextTool, SaveSessionTool, RestoreBackupTool

# Terminal tools
from .terminal import (
    CdTool,
    LsTool as TerminalLsTool,
    PwdTool,
    MkdirTool,
    RmTool,
    CpTool,
    MvTool,
    TouchTool,
    CatTool,
)

# Validated tool base
from .validated import ValidatedTool

__all__ = [
    # Base
    "Tool",
    "ToolCategory",
    "ToolResult",
    "ToolRegistry",
    "ValidatedTool",
    # File ops
    "ReadFileTool",
    "WriteFileTool",
    "EditFileTool",
    "ListDirectoryTool",
    "DeleteFileTool",
    # File mgmt
    "MoveFileTool",
    "CopyFileTool",
    "CreateDirectoryTool",
    "ReadMultipleFilesTool",
    "InsertLinesTool",
    # Search
    "SearchFilesTool",
    "GetDirectoryTreeTool",
    "GlobTool",
    # Claude parity
    "LSTool",
    "MultiEditTool",
    "WebFetchTool",
    "WebSearchTool",
    "TodoReadTool",
    "TodoWriteTool",
    "NotebookReadTool",
    "NotebookEditTool",
    "BackgroundTaskTool",
    "TaskTool",
    "AskUserQuestionTool",
    "get_claude_parity_tools",
    # Plan mode
    "EnterPlanModeTool",
    "ExitPlanModeTool",
    "AddPlanNoteTool",
    "GetPlanStatusTool",
    "get_plan_mode_tools",
    "get_plan_state",
    "reset_plan_state",
    # Execution
    "BashCommandTool",
    # Git
    "GitStatusTool",
    "GitDiffTool",
    # Context
    "GetContextTool",
    "SaveSessionTool",
    "RestoreBackupTool",
    # Terminal
    "CdTool",
    "TerminalLsTool",
    "PwdTool",
    "MkdirTool",
    "RmTool",
    "CpTool",
    "MvTool",
    "TouchTool",
    "CatTool",
]
