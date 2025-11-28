"""
Git Workflow Tools - Modular Architecture
==========================================

Decomposed from git_workflow.py (841 lines) into focused modules.

Modules:
- safety.py: GitSafetyConfig, validate_git_command
- inspect_tools.py: GitStatusEnhancedTool, GitLogTool, GitDiffEnhancedTool
- mutate_tools.py: GitCommitTool, GitPRCreateTool

Author: JuanCS Dev
Date: 2025-11-27
"""

from jdev_cli.tools.git.safety import (
    GitSafetyConfig,
    GitSafetyError,
    validate_git_command,
    get_safety_config,
)
from jdev_cli.tools.git.inspect_tools import (
    GitStatusEnhancedTool,
    GitLogTool,
    GitDiffEnhancedTool,
    get_git_inspect_tools,
)
from jdev_cli.tools.git.mutate_tools import (
    GitCommitTool,
    GitPRCreateTool,
    get_git_mutate_tools,
)

from jdev_cli.tools.base import Tool
from typing import List


def get_git_workflow_tools() -> List[Tool]:
    """
    Get all git workflow tools.

    Returns:
        List of all git tools for registration
    """
    return [
        *get_git_inspect_tools(),
        *get_git_mutate_tools(),
    ]


__all__ = [
    # Safety
    "GitSafetyConfig",
    "GitSafetyError",
    "validate_git_command",
    "get_safety_config",
    # Inspect Tools
    "GitStatusEnhancedTool",
    "GitLogTool",
    "GitDiffEnhancedTool",
    # Mutate Tools
    "GitCommitTool",
    "GitPRCreateTool",
    # Registry
    "get_git_workflow_tools",
    "get_git_inspect_tools",
    "get_git_mutate_tools",
]
