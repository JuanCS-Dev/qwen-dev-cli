"""
Parity Utilities - Shared Components for Claude Parity Tools
============================================================

Extracted from claude_parity_tools.py for code reuse.

Contains:
- TaskTracker: Thread-safe background task state management
- HTMLConverter: HTML to text/markdown conversion
- Constants: Shared configuration values

Author: JuanCS Dev
Date: 2025-11-27
"""

from __future__ import annotations

import html
import logging
import re
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_USER_AGENT = "JuanCS-DevCode/1.0"
DEFAULT_CACHE_TTL = 900  # 15 minutes
SKILL_CACHE_TTL = 60.0   # 1 minute

# Maximum sizes for DoS prevention
MAX_FETCH_SIZE = 10_000_000  # 10MB
MAX_COMMIT_MESSAGE = 1_000_000  # 1MB

# Command search paths for skills/slash commands
COMMAND_SEARCH_PATHS = [
    ".claude/commands",
    ".jdev/commands",
]


# =============================================================================
# TASK TRACKER - Thread-safe state management
# =============================================================================

class TaskTracker:
    """
    Thread-safe task state management for background processes.

    Used by BackgroundTaskTool, BashOutputTool, KillShellTool.

    Example:
        tracker = TaskTracker()
        task_id = tracker.create_task("sleep 10", proc)
        task = tracker.get_task(task_id)
        tracker.cleanup_old_tasks(max_age=3600)
    """

    _instance: Optional['TaskTracker'] = None
    _lock = threading.RLock()

    def __new__(cls) -> 'TaskTracker':
        """Singleton pattern for shared state."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks: Dict[str, Dict[str, Any]] = {}
                    cls._instance._counter = 0
        return cls._instance

    def create_task(
        self,
        command: str,
        process: Any = None,
        status: str = "running"
    ) -> str:
        """
        Create a new task entry.

        Args:
            command: The command being executed
            process: The subprocess.Popen object
            status: Initial status (default: running)

        Returns:
            Unique task ID
        """
        with self._lock:
            self._counter += 1
            task_id = f"task_{self._counter}"
            self._tasks[task_id] = {
                "id": task_id,
                "command": command,
                "process": process,
                "status": status,
                "stdout": [],
                "stderr": [],
                "return_code": None,
                "started_at": time.time(),
                "completed_at": None,
            }
            logger.debug(f"Created task {task_id}: {command[:50]}...")
            return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task dict or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)

    def find_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Find task by ID with 'task_' prefix fallback.

        Args:
            task_id: Task identifier (with or without prefix)

        Returns:
            Task dict or None if not found
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                return task
            # Try with prefix
            prefixed_id = f"task_{task_id}"
            return self._tasks.get(prefixed_id)

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tasks, optionally filtered by status.

        Args:
            status: Filter by status (running, completed, failed, killed)

        Returns:
            List of task dicts
        """
        with self._lock:
            tasks = list(self._tasks.values())
            if status:
                tasks = [t for t in tasks if t.get("status") == status]
            return tasks

    def update_status(
        self,
        task_id: str,
        status: str,
        return_code: Optional[int] = None
    ) -> bool:
        """
        Update task status.

        Args:
            task_id: Task identifier
            status: New status
            return_code: Optional return code

        Returns:
            True if updated, False if not found
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task["status"] = status
            if return_code is not None:
                task["return_code"] = return_code
            if status in ("completed", "failed", "killed"):
                task["completed_at"] = time.time()
            return True

    def append_output(
        self,
        task_id: str,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None
    ) -> bool:
        """
        Append output to task.

        Args:
            task_id: Task identifier
            stdout: Standard output line
            stderr: Standard error line

        Returns:
            True if appended, False if not found
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            if stdout:
                task["stdout"].append(stdout)
            if stderr:
                task["stderr"].append(stderr)
            return True

    def cleanup_old_tasks(self, max_age: int = 3600) -> int:
        """
        Remove tasks older than max_age seconds.

        Args:
            max_age: Maximum age in seconds

        Returns:
            Number of tasks removed
        """
        with self._lock:
            now = time.time()
            old_ids = [
                task_id for task_id, task in self._tasks.items()
                if (now - task.get("started_at", now)) > max_age
                and task.get("status") in ("completed", "failed", "killed")
            ]
            for task_id in old_ids:
                del self._tasks[task_id]
            if old_ids:
                logger.debug(f"Cleaned up {len(old_ids)} old tasks")
            return len(old_ids)

    def clear_all(self) -> None:
        """Clear all tasks (for testing)."""
        with self._lock:
            self._tasks.clear()
            self._counter = 0


# =============================================================================
# HTML CONVERTER
# =============================================================================

class HTMLConverter:
    """
    HTML to text/markdown conversion utilities.

    Used by WebFetchTool, WebSearchTool for processing web content.
    """

    # Common HTML entities
    ENTITIES = {
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": '"',
        "&apos;": "'",
        "&mdash;": "—",
        "&ndash;": "–",
        "&hellip;": "...",
        "&copy;": "©",
        "&reg;": "®",
        "&trade;": "™",
    }

    @classmethod
    def decode_entities(cls, text: str) -> str:
        """
        Decode HTML entities in text.

        Args:
            text: Text with HTML entities

        Returns:
            Decoded text
        """
        # Use html.unescape for standard entities
        text = html.unescape(text)
        # Handle any remaining custom entities
        for entity, char in cls.ENTITIES.items():
            text = text.replace(entity, char)
        return text

    @classmethod
    def to_text(cls, html_content: str, max_length: Optional[int] = None) -> str:
        """
        Convert HTML to plain text.

        Args:
            html_content: HTML string
            max_length: Optional maximum length

        Returns:
            Plain text
        """
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Replace block elements with newlines
        text = re.sub(r'<(?:br|p|div|h\d|li|tr)[^>]*>', '\n', text, flags=re.IGNORECASE)

        # Remove all remaining tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode entities
        text = cls.decode_entities(text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."

        return text

    @classmethod
    def to_markdown(cls, html_content: str, max_length: Optional[int] = None) -> str:
        """
        Convert HTML to markdown-like format.

        Args:
            html_content: HTML string
            max_length: Optional maximum length

        Returns:
            Markdown-formatted text
        """
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert headers
        for i in range(1, 7):
            text = re.sub(
                rf'<h{i}[^>]*>(.*?)</h{i}>',
                rf'\n{"#" * i} \1\n',
                text,
                flags=re.DOTALL | re.IGNORECASE
            )

        # Convert links
        text = re.sub(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            r'[\2](\1)',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        # Convert bold/strong
        text = re.sub(r'<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>', r'**\1**', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert italic/em
        text = re.sub(r'<(?:i|em)[^>]*>(.*?)</(?:i|em)>', r'*\1*', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert code
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert list items
        text = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert paragraphs and breaks
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\1\n', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

        # Remove remaining tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode entities
        text = cls.decode_entities(text)

        # Normalize whitespace
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        if max_length and len(text) > max_length:
            text = text[:max_length] + "..."

        return text


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_USER_AGENT",
    "DEFAULT_CACHE_TTL",
    "SKILL_CACHE_TTL",
    "MAX_FETCH_SIZE",
    "MAX_COMMIT_MESSAGE",
    "COMMAND_SEARCH_PATHS",
    # Classes
    "TaskTracker",
    "HTMLConverter",
]
