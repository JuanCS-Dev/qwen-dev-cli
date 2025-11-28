"""Tool implementations.

This module provides all tools for the Juan-Dev-Code CLI.

Tool Categories:
- File Operations: ReadFileTool, WriteFileTool, EditFileTool, etc.
- Search: SearchFilesTool, GlobTool, GrepTool
- Execution: BashCommandTool, BackgroundTaskTool
- Git: GitStatusTool, GitDiffTool, GitCommitTool, GitPRCreateTool
- Context: GetContextTool, MemoryReadTool, MemoryWriteTool
- Planning: EnterPlanModeTool, ExitPlanModeTool
- User Interaction: AskUserQuestionTool
- Web: WebFetchTool, WebSearchTool
- Notebooks: NotebookReadTool, NotebookEditTool
- Media: ImageReadTool, PDFReadTool
- Subagents: TaskTool

Claude Code Parity (Sprints 1-3):
- Memory system (CLAUDE.md/MEMORY.md)
- AskUserQuestion for user interaction
- Edit replace_all for bulk replacements
- NotebookEdit for Jupyter notebooks
- EnterPlanMode/ExitPlanMode for structured planning
- Task tool with resume capability
- Image/PDF reading (Sprint 3)
- Git commit workflow with safety protocols (Sprint 3)
- Context auto-compact (Sprint 3)
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

# Media tools (Sprint 3)
from .media_tools import (
    ImageReadTool,
    PDFReadTool,
    ScreenshotReadTool,
    get_media_tools,
)

# Git workflow tools (Sprint 3)
from .git_workflow import (
    GitStatusEnhancedTool,
    GitCommitTool,
    GitLogTool,
    GitDiffEnhancedTool,
    GitPRCreateTool,
    get_git_workflow_tools,
    validate_git_command,
)

# Execution tools
from .exec_hardened import BashCommandTool

# Git tools (legacy)
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

def get_all_tools():
    """Get all available tools for agents."""
    return [
        # File operations
        ReadFileTool(),
        WriteFileTool(),
        EditFileTool(),
        ListDirectoryTool(),
        DeleteFileTool(),
        MoveFileTool(),
        CopyFileTool(),
        CreateDirectoryTool(),
        ReadMultipleFilesTool(),
        InsertLinesTool(),
        # Search
        SearchFilesTool(),
        GetDirectoryTreeTool(),
        GlobTool(),
        # Execution
        BashCommandTool(),
        BackgroundTaskTool(),
        # Git
        GitStatusTool(),
        GitDiffTool(),
        GitStatusEnhancedTool(),
        GitCommitTool(),
        GitLogTool(),
        GitDiffEnhancedTool(),
        GitPRCreateTool(),
        # Context
        GetContextTool(),
        SaveSessionTool(),
        RestoreBackupTool(),
        # Claude parity
        LSTool(),
        MultiEditTool(),
        WebFetchTool(),
        WebSearchTool(),
        TodoReadTool(),
        TodoWriteTool(),
        NotebookReadTool(),
        NotebookEditTool(),
        TaskTool(),
        AskUserQuestionTool(),
        # Plan mode
        EnterPlanModeTool(),
        ExitPlanModeTool(),
        AddPlanNoteTool(),
        GetPlanStatusTool(),
        # Media
        ImageReadTool(),
        PDFReadTool(),
        ScreenshotReadTool(),
        # Terminal
        CdTool(),
        TerminalLsTool(),
        PwdTool(),
        MkdirTool(),
        RmTool(),
        CpTool(),
        MvTool(),
        TouchTool(),
        CatTool(),
    ]


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
    # Media tools (Sprint 3)
    "ImageReadTool",
    "PDFReadTool",
    "ScreenshotReadTool",
    "get_media_tools",
    # Git workflow (Sprint 3)
    "GitStatusEnhancedTool",
    "GitCommitTool",
    "GitLogTool",
    "GitDiffEnhancedTool",
    "GitPRCreateTool",
    "get_git_workflow_tools",
    "validate_git_command",
    # Execution
    "BashCommandTool",
    # Git (legacy)
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
    # Utility
    "get_all_tools",
]
