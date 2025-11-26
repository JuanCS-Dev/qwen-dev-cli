"""Git Workflow Tools - Complete git operations for Claude Code parity.

Claude Code parity: Implements git commit workflow with:
- Pre-commit checks
- Commit message generation
- PR creation support
- Safety protocols (no force push to main, etc.)

Author: Juan CS
Date: 2025-11-26
"""

from __future__ import annotations

import asyncio
import logging
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import Tool, ToolCategory, ToolResult

logger = logging.getLogger(__name__)


# =============================================================================
# GIT SAFETY PROTOCOLS
# =============================================================================

class GitSafetyError(Exception):
    """Raised when a git operation violates safety protocols."""
    pass


@dataclass
class GitSafetyConfig:
    """Configuration for git safety protocols.

    Claude Code safety rules:
    - NEVER update git config
    - NEVER run destructive commands (push --force, hard reset)
    - NEVER skip hooks (--no-verify)
    - NEVER force push to main/master
    - Avoid git commit --amend unless explicitly requested
    """

    # Protected branches (no force push)
    protected_branches: List[str] = field(default_factory=lambda: ["main", "master", "develop"])

    # Dangerous flags to block
    dangerous_flags: List[str] = field(default_factory=lambda: [
        "--force", "-f",
        "--hard",
        "--no-verify",
        "--no-gpg-sign",
        "-i",  # Interactive (not supported)
    ])

    # Dangerous commands to block
    dangerous_commands: List[str] = field(default_factory=lambda: [
        "config",  # Never modify git config
        "push --force",
        "push -f",
        "reset --hard",
        "clean -fd",
        "checkout -f",
    ])


# Global safety config
_git_safety = GitSafetyConfig()


def validate_git_command(command: str) -> Tuple[bool, str]:
    """Validate a git command against safety protocols.

    Args:
        command: Full git command string

    Returns:
        Tuple of (is_safe, reason)
    """
    cmd_lower = command.lower()

    # Check dangerous commands
    for dangerous in _git_safety.dangerous_commands:
        if dangerous in cmd_lower:
            return False, f"Blocked: '{dangerous}' violates safety protocol"

    # Check dangerous flags
    for flag in _git_safety.dangerous_flags:
        if f" {flag}" in command or command.endswith(flag):
            return False, f"Blocked: '{flag}' flag violates safety protocol"

    # Check force push to protected branches
    if "push" in cmd_lower and ("--force" in cmd_lower or "-f" in cmd_lower):
        for branch in _git_safety.protected_branches:
            if branch in cmd_lower:
                return False, f"Blocked: Force push to '{branch}' not allowed"

    return True, "OK"


# =============================================================================
# GIT STATUS TOOL (Enhanced)
# =============================================================================

class GitStatusEnhancedTool(Tool):
    """Enhanced git status with detailed information.

    Returns:
    - Current branch
    - Tracking branch status
    - Staged/unstaged/untracked files
    - Ahead/behind counts
    """

    def __init__(self):
        super().__init__()
        self.name = "git_status_enhanced"
        self.category = ToolCategory.GIT
        self.description = "Get detailed git status information"
        self.parameters = {
            "include_diff_stats": {
                "type": "boolean",
                "description": "Include diff statistics (default: False)",
                "required": False
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Get enhanced git status."""
        include_diff_stats = kwargs.get("include_diff_stats", False)

        try:
            # Get current branch
            branch_result = await self._run_git("rev-parse", "--abbrev-ref", "HEAD")
            current_branch = branch_result.stdout.strip() if branch_result.success else "unknown"

            # Get status
            status_result = await self._run_git("status", "--porcelain=v2", "--branch")

            if not status_result.success:
                return ToolResult(success=False, error=status_result.stderr)

            # Parse status
            parsed = self._parse_status_v2(status_result.stdout)

            # Get tracking info
            tracking_result = await self._run_git(
                "rev-list", "--left-right", "--count", f"{current_branch}@{{u}}...HEAD"
            )

            ahead, behind = 0, 0
            if tracking_result.success:
                parts = tracking_result.stdout.strip().split()
                if len(parts) == 2:
                    behind, ahead = int(parts[0]), int(parts[1])

            # Get diff stats if requested
            diff_stats = None
            if include_diff_stats and (parsed["staged"] or parsed["modified"]):
                diff_result = await self._run_git("diff", "--stat", "--cached")
                if diff_result.success:
                    diff_stats = diff_result.stdout

            return ToolResult(
                success=True,
                data={
                    "branch": current_branch,
                    "ahead": ahead,
                    "behind": behind,
                    "is_clean": len(parsed["staged"]) == 0 and len(parsed["modified"]) == 0,
                    "staged": parsed["staged"],
                    "modified": parsed["modified"],
                    "untracked": parsed["untracked"],
                    "deleted": parsed["deleted"],
                    "renamed": parsed["renamed"],
                    "diff_stats": diff_stats,
                    "summary": self._format_summary(parsed, ahead, behind)
                },
                metadata={
                    "file_count": sum(len(v) for v in parsed.values()),
                    "branch": current_branch
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _parse_status_v2(self, output: str) -> Dict[str, List[str]]:
        """Parse git status --porcelain=v2 output."""
        result = {
            "staged": [],
            "modified": [],
            "untracked": [],
            "deleted": [],
            "renamed": [],
        }

        for line in output.split("\n"):
            if not line:
                continue

            if line.startswith("# "):
                continue  # Header line

            if line.startswith("? "):
                # Untracked
                result["untracked"].append(line[2:])
            elif line.startswith("1 ") or line.startswith("2 "):
                # Changed entry
                parts = line.split("\t")
                if len(parts) >= 2:
                    status_part = parts[0].split()
                    xy = status_part[1] if len(status_part) > 1 else ".."
                    path = parts[-1]

                    if xy[0] in "MARC":
                        result["staged"].append(path)
                    if xy[1] == "M":
                        result["modified"].append(path)
                    if xy[1] == "D" or xy[0] == "D":
                        result["deleted"].append(path)
                    if xy[0] == "R":
                        result["renamed"].append(path)

        return result

    def _format_summary(self, parsed: Dict, ahead: int, behind: int) -> str:
        """Format a human-readable summary."""
        parts = []

        if ahead:
            parts.append(f"ahead {ahead}")
        if behind:
            parts.append(f"behind {behind}")
        if parsed["staged"]:
            parts.append(f"{len(parsed['staged'])} staged")
        if parsed["modified"]:
            parts.append(f"{len(parsed['modified'])} modified")
        if parsed["untracked"]:
            parts.append(f"{len(parsed['untracked'])} untracked")
        if parsed["deleted"]:
            parts.append(f"{len(parsed['deleted'])} deleted")

        return ", ".join(parts) if parts else "clean"

    async def _run_git(self, *args) -> ToolResult:
        """Run a git command safely."""
        try:
            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                timeout=30
            )
            return ToolResult(
                success=result.returncode == 0,
                data=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


# =============================================================================
# GIT COMMIT TOOL
# =============================================================================

class GitCommitTool(Tool):
    """Create git commits with Claude Code conventions.

    Features:
    - Validates changes before commit
    - Adds Claude Code signature
    - Respects safety protocols
    - Supports pre-commit hooks

    Commit message format:
    ```
    <type>(<scope>): <description>

    <body>

    🤖 Generated with [Claude Code](https://claude.com/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    ```
    """

    def __init__(self):
        super().__init__()
        self.name = "git_commit"
        self.category = ToolCategory.GIT
        self.description = "Create a git commit with Claude Code conventions"
        self.parameters = {
            "message": {
                "type": "string",
                "description": "Commit message (without signature)",
                "required": True
            },
            "files": {
                "type": "array",
                "description": "Files to stage (default: all modified)",
                "required": False
            },
            "amend": {
                "type": "boolean",
                "description": "Amend previous commit (requires explicit permission)",
                "required": False
            },
            "add_signature": {
                "type": "boolean",
                "description": "Add Claude Code signature (default: True)",
                "required": False
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Create git commit."""
        message = kwargs.get("message", "")
        files = kwargs.get("files", [])
        amend = kwargs.get("amend", False)
        add_signature = kwargs.get("add_signature", True)

        if not message:
            return ToolResult(success=False, error="Commit message is required")

        try:
            # Safety check for amend
            if amend:
                # Check authorship before amending
                author_check = await self._check_authorship()
                if not author_check["safe_to_amend"]:
                    return ToolResult(
                        success=False,
                        error=f"Cannot amend: {author_check['reason']}"
                    )

            # Stage files
            if files:
                for file in files:
                    stage_result = await self._run_git("add", file)
                    if not stage_result.success:
                        return ToolResult(
                            success=False,
                            error=f"Failed to stage {file}: {stage_result.error}"
                        )
            else:
                # Stage all modified files
                stage_result = await self._run_git("add", "-A")
                if not stage_result.success:
                    return ToolResult(success=False, error=f"Failed to stage: {stage_result.error}")

            # Check if there are staged changes
            diff_result = await self._run_git("diff", "--cached", "--quiet")
            if diff_result.success:
                return ToolResult(
                    success=False,
                    error="No changes staged for commit"
                )

            # Build commit message
            full_message = self._build_commit_message(message, add_signature)

            # Create commit
            commit_args = ["commit", "-m", full_message]
            if amend:
                commit_args.append("--amend")

            commit_result = await self._run_git(*commit_args)

            if not commit_result.success:
                # Check if pre-commit hook modified files
                if "pre-commit" in commit_result.error.lower():
                    return ToolResult(
                        success=False,
                        error="Pre-commit hook modified files. Review changes and retry.",
                        data={"hook_triggered": True}
                    )
                return ToolResult(success=False, error=commit_result.error)

            # Get commit hash
            hash_result = await self._run_git("rev-parse", "--short", "HEAD")
            commit_hash = hash_result.data.strip() if hash_result.success else "unknown"

            return ToolResult(
                success=True,
                data={
                    "commit": commit_hash,
                    "message": message,
                    "amended": amend,
                    "files_committed": len(files) if files else "all staged"
                },
                metadata={"hash": commit_hash}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _check_authorship(self) -> Dict[str, Any]:
        """Check if safe to amend previous commit."""
        # Get last commit author
        result = await self._run_git("log", "-1", "--format=%an %ae")
        if not result.success:
            return {"safe_to_amend": False, "reason": "Could not check authorship"}

        author = result.data.strip()

        # Check if pushed
        status_result = await self._run_git("status", "-sb")
        if status_result.success and "ahead" not in status_result.data:
            return {"safe_to_amend": False, "reason": "Commit may already be pushed"}

        # Allow amend for Claude-authored commits or unpushed commits
        if "claude" in author.lower() or "noreply@anthropic.com" in author.lower():
            return {"safe_to_amend": True, "reason": "Claude-authored commit"}

        return {
            "safe_to_amend": True,
            "reason": f"Unpushed commit by {author}",
            "warning": "Amending another developer's commit"
        }

    def _build_commit_message(self, message: str, add_signature: bool) -> str:
        """Build full commit message with optional signature."""
        if not add_signature:
            return message

        signature = """

🤖 Generated with Juan-Dev-Code

Co-Authored-By: Juan-Dev-Code <noreply@juancs.dev>"""

        return message + signature

    async def _run_git(self, *args) -> ToolResult:
        """Run a git command safely."""
        # Validate command
        full_cmd = f"git {' '.join(args)}"
        is_safe, reason = validate_git_command(full_cmd)
        if not is_safe:
            return ToolResult(success=False, error=reason)

        try:
            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                timeout=60
            )
            return ToolResult(
                success=result.returncode == 0,
                data=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git command timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


# =============================================================================
# GIT LOG TOOL
# =============================================================================

class GitLogTool(Tool):
    """Get git commit history.

    Returns recent commits with hash, author, date, and message.
    """

    def __init__(self):
        super().__init__()
        self.name = "git_log"
        self.category = ToolCategory.GIT
        self.description = "Get git commit history"
        self.parameters = {
            "count": {
                "type": "integer",
                "description": "Number of commits to show (default: 10)",
                "required": False
            },
            "oneline": {
                "type": "boolean",
                "description": "One line per commit (default: True)",
                "required": False
            },
            "branch": {
                "type": "string",
                "description": "Branch to show history for (default: current)",
                "required": False
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Get git log."""
        count = kwargs.get("count", 10)
        oneline = kwargs.get("oneline", True)
        branch = kwargs.get("branch", "")

        try:
            args = ["log", f"-{count}"]

            if oneline:
                args.append("--oneline")
            else:
                args.extend(["--format=%H|%an|%ar|%s"])

            if branch:
                args.append(branch)

            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                if oneline:
                    parts = line.split(" ", 1)
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1] if len(parts) > 1 else ""
                    })
                else:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0][:7],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })

            return ToolResult(
                success=True,
                data={"commits": commits},
                metadata={"count": len(commits)}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


# =============================================================================
# GIT DIFF ENHANCED
# =============================================================================

class GitDiffEnhancedTool(Tool):
    """Enhanced git diff with statistics.

    Shows changes between commits, branches, or working tree.
    """

    def __init__(self):
        super().__init__()
        self.name = "git_diff_enhanced"
        self.category = ToolCategory.GIT
        self.description = "Get git diff with statistics"
        self.parameters = {
            "target": {
                "type": "string",
                "description": "Target to diff against (e.g., 'HEAD~1', 'main', 'staged')",
                "required": False
            },
            "stat_only": {
                "type": "boolean",
                "description": "Show only statistics (default: False)",
                "required": False
            },
            "file": {
                "type": "string",
                "description": "Specific file to diff",
                "required": False
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Get git diff."""
        target = kwargs.get("target", "")
        stat_only = kwargs.get("stat_only", False)
        file_path = kwargs.get("file", "")

        try:
            args = ["diff"]

            if target == "staged":
                args.append("--cached")
            elif target:
                args.append(target)

            if stat_only:
                args.append("--stat")

            if file_path:
                args.extend(["--", file_path])

            result = subprocess.run(
                ["git", *args],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)

            # Get stats
            stat_args = ["diff", "--stat"]
            if target == "staged":
                stat_args.append("--cached")
            elif target:
                stat_args.append(target)

            stat_result = subprocess.run(
                ["git", *stat_args],
                capture_output=True,
                text=True,
                timeout=30
            )

            stats = self._parse_diff_stats(stat_result.stdout) if stat_result.returncode == 0 else {}

            return ToolResult(
                success=True,
                data={
                    "diff": result.stdout[:10000] if not stat_only else None,
                    "stats": stat_result.stdout if stat_only else None,
                    "files_changed": stats.get("files", 0),
                    "insertions": stats.get("insertions", 0),
                    "deletions": stats.get("deletions", 0),
                },
                metadata={"target": target or "working tree"}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _parse_diff_stats(self, output: str) -> Dict[str, int]:
        """Parse diff --stat output."""
        # Last line format: "X files changed, Y insertions(+), Z deletions(-)"
        match = re.search(
            r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?',
            output
        )

        if match:
            return {
                "files": int(match.group(1)),
                "insertions": int(match.group(2) or 0),
                "deletions": int(match.group(3) or 0),
            }

        return {"files": 0, "insertions": 0, "deletions": 0}


# =============================================================================
# PR CREATION TOOL
# =============================================================================

class GitPRCreateTool(Tool):
    """Create GitHub Pull Request using gh CLI.

    Claude Code parity: Create PRs with standard format.
    Requires: gh CLI installed and authenticated.
    """

    def __init__(self):
        super().__init__()
        self.name = "git_pr_create"
        self.category = ToolCategory.GIT
        self.description = "Create a GitHub Pull Request"
        self.parameters = {
            "title": {
                "type": "string",
                "description": "PR title",
                "required": True
            },
            "body": {
                "type": "string",
                "description": "PR description (markdown)",
                "required": False
            },
            "base": {
                "type": "string",
                "description": "Base branch (default: main)",
                "required": False
            },
            "draft": {
                "type": "boolean",
                "description": "Create as draft PR",
                "required": False
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Create PR."""
        title = kwargs.get("title", "")
        body = kwargs.get("body", "")
        base = kwargs.get("base", "main")
        draft = kwargs.get("draft", False)

        if not title:
            return ToolResult(success=False, error="PR title is required")

        # Check if gh is available
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ToolResult(
                success=False,
                error="GitHub CLI (gh) not found. Install from: https://cli.github.com"
            )

        try:
            # Build PR body
            full_body = self._build_pr_body(body)

            args = [
                "gh", "pr", "create",
                "--title", title,
                "--body", full_body,
                "--base", base,
            ]

            if draft:
                args.append("--draft")

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return ToolResult(success=False, error=result.stderr)

            # Extract PR URL
            pr_url = result.stdout.strip()

            return ToolResult(
                success=True,
                data={
                    "url": pr_url,
                    "title": title,
                    "base": base,
                    "draft": draft,
                },
                metadata={"created": True}
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _build_pr_body(self, body: str) -> str:
        """Build PR body with Juan-Dev-Code signature."""
        signature = "\n\n🤖 Generated with Juan-Dev-Code"

        if not body:
            return f"## Summary\n\n_No description provided._\n{signature}"

        return body + signature


# =============================================================================
# REGISTRY HELPER
# =============================================================================

def get_git_workflow_tools() -> List[Tool]:
    """Get all git workflow tools."""
    return [
        GitStatusEnhancedTool(),
        GitCommitTool(),
        GitLogTool(),
        GitDiffEnhancedTool(),
        GitPRCreateTool(),
    ]
