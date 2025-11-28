"""
Git Safety - Security Protocols for Git Operations
===================================================

Contains:
- GitSafetyConfig: Configuration for safety rules
- GitSafetyError: Exception for safety violations
- validate_git_command: Command validator

Claude Code Safety Rules:
- NEVER update git config
- NEVER run destructive commands (push --force, hard reset)
- NEVER skip hooks (--no-verify)
- NEVER force push to main/master
- Avoid git commit --amend unless explicitly requested

Author: JuanCS Dev
Date: 2025-11-27
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class GitSafetyError(Exception):
    """Raised when a git operation violates safety protocols."""
    pass


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class GitSafetyConfig:
    """
    Configuration for git safety protocols.

    Attributes:
        protected_branches: Branches where force push is blocked
        dangerous_flags: Command flags that are blocked
        dangerous_commands: Command patterns that are blocked

    Example:
        config = GitSafetyConfig(
            protected_branches=["main", "master", "production"],
            dangerous_flags=["--force", "-f", "--hard"]
        )
    """

    # Protected branches (no force push)
    protected_branches: List[str] = field(default_factory=lambda: [
        "main",
        "master",
        "develop",
        "production",
        "release",
    ])

    # Dangerous flags to block
    dangerous_flags: List[str] = field(default_factory=lambda: [
        "--force",
        "-f",
        "--hard",
        "--no-verify",
        "--no-gpg-sign",
        "-i",  # Interactive (not supported in automated context)
    ])

    # Dangerous commands to block
    dangerous_commands: List[str] = field(default_factory=lambda: [
        "config",           # Never modify git config
        "push --force",
        "push -f",
        "reset --hard",
        "clean -fd",
        "checkout -f",
        "rebase -i",        # Interactive rebase not supported
        "filter-branch",    # History rewriting
        "gc --prune",       # Aggressive garbage collection
    ])

    # Maximum commit message size (DoS prevention)
    max_commit_message: int = 1_000_000  # 1MB

    def add_protected_branch(self, branch: str) -> None:
        """Add a branch to protected list."""
        if branch not in self.protected_branches:
            self.protected_branches.append(branch)
            logger.info(f"Added protected branch: {branch}")

    def is_branch_protected(self, branch: str) -> bool:
        """Check if a branch is protected."""
        return branch.lower() in [b.lower() for b in self.protected_branches]


# Global safety config (singleton)
_git_safety_config: GitSafetyConfig = None


def get_safety_config() -> GitSafetyConfig:
    """Get the global git safety configuration."""
    global _git_safety_config
    if _git_safety_config is None:
        _git_safety_config = GitSafetyConfig()
    return _git_safety_config


def set_safety_config(config: GitSafetyConfig) -> None:
    """Set the global git safety configuration (for testing)."""
    global _git_safety_config
    _git_safety_config = config


# =============================================================================
# VALIDATION
# =============================================================================

def validate_git_command(command: str) -> Tuple[bool, str]:
    """
    Validate a git command against safety protocols.

    Args:
        command: Full git command string (e.g., "git push --force origin main")

    Returns:
        Tuple of (is_safe, reason)
            - is_safe: True if command passes safety checks
            - reason: "OK" if safe, or explanation of violation

    Example:
        is_safe, reason = validate_git_command("git push --force origin main")
        if not is_safe:
            raise GitSafetyError(reason)
    """
    config = get_safety_config()
    cmd_lower = command.lower()

    # Check dangerous commands
    for dangerous in config.dangerous_commands:
        if dangerous in cmd_lower:
            logger.warning(f"Git safety: blocked '{dangerous}'")
            return False, f"Blocked: '{dangerous}' violates safety protocol"

    # Check dangerous flags
    for flag in config.dangerous_flags:
        # Check with space before (to avoid matching partial words)
        if f" {flag}" in command or command.endswith(flag):
            # Exception: --force is allowed for git fetch
            if flag in ("--force", "-f") and "fetch" in cmd_lower:
                continue
            logger.warning(f"Git safety: blocked flag '{flag}'")
            return False, f"Blocked: '{flag}' flag violates safety protocol"

    # Check force push to protected branches
    if "push" in cmd_lower and ("--force" in cmd_lower or "-f " in cmd_lower):
        for branch in config.protected_branches:
            if branch.lower() in cmd_lower:
                logger.warning(f"Git safety: force push to protected branch '{branch}'")
                return False, f"Blocked: Force push to '{branch}' not allowed"

    # Check for git config modification
    if "config" in cmd_lower and "git" in cmd_lower:
        # Allow git config --get (read-only)
        if "--get" not in cmd_lower and "--list" not in cmd_lower:
            logger.warning("Git safety: config modification blocked")
            return False, "Blocked: Git config modification not allowed"

    return True, "OK"


def validate_commit_message(message: str) -> Tuple[bool, str]:
    """
    Validate a commit message.

    Args:
        message: Commit message text

    Returns:
        Tuple of (is_valid, reason)
    """
    config = get_safety_config()

    if not message or not message.strip():
        return False, "Commit message cannot be empty"

    if len(message) > config.max_commit_message:
        return False, f"Commit message too large ({len(message)} > {config.max_commit_message})"

    return True, "OK"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GitSafetyConfig",
    "GitSafetyError",
    "validate_git_command",
    "validate_commit_message",
    "get_safety_config",
    "set_safety_config",
]
