"""
PullRequestManager - GitHub PR Operations.

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Manages:
- PR creation via gh CLI
- PR templates
- Authentication checks

Author: JuanCS Dev
Date: 2025-11-26
"""

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from jdev_tui.core.interfaces import IPullRequestManager


class PullRequestManager(IPullRequestManager):
    """
    GitHub Pull Request manager.

    Implements IPullRequestManager interface for:
    - Creating pull requests via gh CLI
    - Reading PR templates
    - Checking GitHub authentication
    """

    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize PullRequestManager.

        Args:
            working_dir: Working directory for git operations. Defaults to cwd.
        """
        self._working_dir = working_dir or Path.cwd()

    async def create_pull_request(
        self,
        title: str,
        body: Optional[str] = None,
        base: str = "main",
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Create a GitHub pull request using gh CLI.

        Args:
            title: PR title.
            body: PR body/description.
            base: Base branch for the PR.
            draft: If True, create as draft PR.

        Returns:
            Dictionary with success status and PR details.
        """
        # Check if gh is available
        if not shutil.which("gh"):
            return {
                "success": False,
                "error": "GitHub CLI (gh) not installed. Install with: brew install gh"
            }

        # Check if authenticated
        try:
            auth_check = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self._working_dir)
            )
            if auth_check.returncode != 0:
                return {
                    "success": False,
                    "error": "Not authenticated with GitHub. Run: gh auth login"
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "GitHub auth check timed out"}
        except Exception as e:
            return {"success": False, "error": f"Auth check failed: {e}"}

        # Get current branch
        current_branch = self._get_current_branch()

        # Build PR body if not provided
        if not body:
            body = self._generate_default_body(title)

        # Create PR command
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]

        if draft:
            cmd.append("--draft")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self._working_dir)
            )

            if result.returncode == 0:
                pr_url = result.stdout.strip()
                return {
                    "success": True,
                    "url": pr_url,
                    "branch": current_branch,
                    "base": base,
                    "draft": draft,
                    "message": f"PR created: {pr_url}"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or "PR creation failed",
                    "stdout": result.stdout
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "PR creation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_pr_template(self) -> str:
        """
        Get PR template if exists.

        Returns:
            Template content or empty string.
        """
        templates = [
            self._working_dir / ".github" / "pull_request_template.md",
            self._working_dir / ".github" / "PULL_REQUEST_TEMPLATE.md",
            self._working_dir / "pull_request_template.md",
        ]

        for template in templates:
            if template.exists():
                try:
                    return template.read_text()
                except Exception:
                    continue

        return ""

    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self._working_dir)
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def _generate_default_body(self, title: str) -> str:
        """Generate default PR body."""
        return f"""## Summary
{title}

## Changes
- See commit history for details

## Test Plan
- [ ] Tests pass
- [ ] Manual testing done

---
🤖 Generated with [JuanCS Dev-Code](https://github.com/juancs/dev-code)
"""

    def is_gh_available(self) -> bool:
        """Check if gh CLI is available."""
        return shutil.which("gh") is not None

    def is_authenticated(self) -> bool:
        """Check if authenticated with GitHub."""
        if not self.is_gh_available():
            return False

        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
