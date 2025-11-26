"""
shell/safety.py: Command Safety Evaluation.

Extracted from shell_main.py for modularity.
Implements Claude pattern: tiered confirmations.
"""

from __future__ import annotations

import re
from typing import Set


# Safety levels
SAFE_COMMANDS: Set[str] = {
    'ls', 'pwd', 'echo', 'cat', 'head', 'tail',
    'grep', 'find', 'df', 'du', 'ps', 'top',
    'date', 'whoami', 'hostname', 'uname',
    'which', 'whereis', 'file', 'stat', 'wc',
}

DANGEROUS_COMMANDS: Set[str] = {
    'rm', 'rmdir', 'dd', 'mkfs', 'fdisk', 'format',
    ':(){:|:&};:', 'shutdown', 'reboot', 'init',
    'kill', 'pkill', 'killall',
}


def get_safety_level(command: str) -> int:
    """
    Get safety level (Claude pattern: tiered confirmations).

    Levels:
        0: Safe (auto-execute with default yes)
        1: Confirm once (standard operations)
        2: Dangerous (double confirmation)

    Args:
        command: The shell command to evaluate

    Returns:
        Safety level (0, 1, or 2)
    """
    if not command:
        return 1

    # Check for dangerous commands anywhere in the command string (handles chains)
    tokens = re.split(r'[;&|]', command)

    has_dangerous = False
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        cmd = token.split()[0]
        if cmd in DANGEROUS_COMMANDS:
            has_dangerous = True
            break

    if has_dangerous:
        return 2

    # Check if first command is safe (only if all commands are safe)
    first_cmd = command.split()[0] if command else ""
    if first_cmd in SAFE_COMMANDS:
        return 0

    return 1  # Default: confirm once


def is_safe(command: str) -> bool:
    """Check if command is safe (level 0)."""
    return get_safety_level(command) == 0


def is_dangerous(command: str) -> bool:
    """Check if command is dangerous (level 2)."""
    return get_safety_level(command) == 2


def needs_confirmation(command: str) -> bool:
    """Check if command needs any confirmation (level > 0)."""
    return get_safety_level(command) > 0


def get_safety_description(level: int) -> str:
    """Get human-readable description for safety level."""
    descriptions = {
        0: "Safe - auto-execute with default yes",
        1: "Standard - requires single confirmation",
        2: "Dangerous - requires double confirmation",
    }
    return descriptions.get(level, "Unknown safety level")
