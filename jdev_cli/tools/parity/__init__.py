"""
Claude Code Parity Tools - Modular Architecture
================================================

Decomposed from claude_parity_tools.py (2069 lines) into focused modules.

Modules:
- file_tools: GlobTool, LSTool, MultiEditTool
- web_tools: WebFetchTool, WebSearchTool
- notebook_tools: NotebookReadTool, NotebookEditTool
- todo_tools: TodoReadTool, TodoWriteTool
- execution_tools: BackgroundTaskTool, BashOutputTool, KillShellTool
- interaction_tools: AskUserQuestionTool, SkillTool, SlashCommandTool
- task_tool: TaskTool (subagents)

Author: JuanCS Dev
Date: 2025-11-27
"""

from jdev_cli.tools.parity.file_tools import (
    GlobTool,
    LSTool,
    MultiEditTool,
    get_file_tools,
)
from jdev_cli.tools.parity.web_tools import (
    WebFetchTool,
    WebSearchTool,
    get_web_tools,
)
from jdev_cli.tools.parity.notebook_tools import (
    NotebookReadTool,
    NotebookEditTool,
    get_notebook_tools,
)
from jdev_cli.tools.parity.todo_tools import (
    TodoReadTool,
    TodoWriteTool,
    get_todo_tools,
)
from jdev_cli.tools.parity.execution_tools import (
    BackgroundTaskTool,
    BashOutputTool,
    KillShellTool,
    get_execution_tools,
)
from jdev_cli.tools.parity.interaction_tools import (
    AskUserQuestionTool,
    SkillTool,
    SlashCommandTool,
    get_interaction_tools,
)
from jdev_cli.tools.parity.task_tool import (
    TaskTool,
)

from jdev_cli.tools.base import Tool
from typing import List


def get_claude_parity_tools() -> List[Tool]:
    """
    Get all Claude Code parity tools.

    Returns:
        List of all parity tools for registration
    """
    return [
        *get_file_tools(),
        *get_web_tools(),
        *get_notebook_tools(),
        *get_todo_tools(),
        *get_execution_tools(),
        *get_interaction_tools(),
        TaskTool(),
    ]


__all__ = [
    # File Tools
    "GlobTool",
    "LSTool",
    "MultiEditTool",
    # Web Tools
    "WebFetchTool",
    "WebSearchTool",
    # Notebook Tools
    "NotebookReadTool",
    "NotebookEditTool",
    # Todo Tools
    "TodoReadTool",
    "TodoWriteTool",
    # Execution Tools
    "BackgroundTaskTool",
    "BashOutputTool",
    "KillShellTool",
    # Interaction Tools
    "AskUserQuestionTool",
    "SkillTool",
    "SlashCommandTool",
    # Task/Subagent Tool
    "TaskTool",
    # Registry
    "get_claude_parity_tools",
    # Module getters
    "get_file_tools",
    "get_web_tools",
    "get_notebook_tools",
    "get_todo_tools",
    "get_execution_tools",
    "get_interaction_tools",
]
