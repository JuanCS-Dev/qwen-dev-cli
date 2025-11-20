"""Hooks system for automated post-action execution.

This module provides a complete hooks system that allows automated
execution of commands after file operations (write, edit, delete) and
before git operations (commit).

Features:
- Variable substitution in commands ({file}, {dir}, etc)
- Safe command whitelist (execute directly for performance)
- Dangerous command sandbox (Docker isolation for security)
- Async execution with timeout
- Comprehensive logging and statistics

Example:
    >>> from qwen_dev_cli.hooks import HookExecutor, HookEvent, HookContext
    >>> from pathlib import Path
    >>>
    >>> executor = HookExecutor()
    >>> context = HookContext(Path("src/test.py"), "post_write")
    >>> hooks = ["black {file}", "ruff check {file}"]
    >>>
    >>> results = await executor.execute_hooks(
    ...     HookEvent.POST_WRITE, context, hooks
    ... )
"""

from .events import HookEvent, HookPriority
from .context import HookContext
from .whitelist import SafeCommandWhitelist
from .executor import HookExecutor, HookResult

__all__ = [
    'HookEvent',
    'HookPriority',
    'HookContext',
    'SafeCommandWhitelist',
    'HookExecutor',
    'HookResult',
]

__version__ = '1.0.0'
