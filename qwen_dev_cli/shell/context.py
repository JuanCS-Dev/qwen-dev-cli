"""
shell/context.py: Session Context Management.

Extracted from shell_main.py for modularity.
Contains session-level state tracking for the interactive shell.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Set


class SessionContext:
    """
    Persistent context across shell session.

    Tracks:
    - Current working directory
    - Conversation history
    - Modified/read files
    - Tool call history
    """

    def __init__(self):
        try:
            self.cwd = os.getcwd()
        except (FileNotFoundError, OSError):
            # CWD may not exist (e.g., deleted temp dir)
            # Fallback to home or /tmp
            self.cwd = os.path.expanduser("~")

        self.conversation: List[Dict[str, Any]] = []
        self.modified_files: Set[str] = set()
        self.read_files: Set[str] = set()
        self.tool_calls: List[Dict[str, Any]] = []
        self.history: List[str] = []

        # Week 2 Integration: Preview settings
        self.preview_enabled: bool = True

    def track_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        result: Any
    ) -> None:
        """
        Track tool usage for session analytics.

        Args:
            tool_name: Name of the executed tool
            args: Arguments passed to the tool
            result: Tool execution result
        """
        self.tool_calls.append({
            "tool": tool_name,
            "args": args,
            "result": result,
            "success": getattr(result, 'success', True)
        })

        # Track file operations
        if tool_name in ("write_file", "edit_file"):
            path = args.get("path", "")
            if path:
                self.modified_files.add(path)
        elif tool_name == "read_file":
            path = args.get("path", "")
            if path:
                self.read_files.add(path)

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        successful_calls = sum(1 for call in self.tool_calls if call.get("success"))

        return {
            "cwd": self.cwd,
            "conversation_turns": len(self.conversation),
            "modified_files_count": len(self.modified_files),
            "read_files_count": len(self.read_files),
            "tool_calls_total": len(self.tool_calls),
            "tool_calls_success": successful_calls,
            "history_length": len(self.history),
            "preview_enabled": self.preview_enabled,
        }

    def reset(self) -> None:
        """Reset session context (preserves cwd)."""
        self.conversation.clear()
        self.modified_files.clear()
        self.read_files.clear()
        self.tool_calls.clear()
        self.history.clear()
