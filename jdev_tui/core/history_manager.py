"""
HistoryManager - Command and Session History Management
=======================================================

Extracted from Bridge GOD CLASS (Nov 2025 Refactoring).

Features:
- Persistent command history (~/.jdev_tui_history)
- Session-based conversation context
- Smart history search
- Session save/load/list (Claude Code parity: /resume, /rewind)
- Checkpoint system for conversation rewinding
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Command and conversation history management.

    Features:
    - Persistent command history
    - Session-based conversation context
    - Smart history search
    - Session persistence (save/load/list)
    - Checkpoint system for rewinding
    - **NEW**: Context compaction (Claude Code Parity - Nov 2025)

    Usage:
        history = HistoryManager()
        history.add_command("git status")
        history.add_context("user", "Check the git status")
        history.add_context("assistant", "Running git status...")
        history.save_session()
    """

    # Maximum checkpoints to prevent memory leak (AIR GAP FIX)
    MAX_CHECKPOINTS = 20

    # Context compaction thresholds (Claude Code Parity)
    MAX_CONTEXT_TOKENS = 32000  # Default context window
    COMPACTION_THRESHOLD = 0.60  # Trigger compaction at 60%
    CHARS_PER_TOKEN = 4  # Rough estimate for token counting

    def __init__(
        self,
        max_commands: int = 1000,
        max_context: int = 50,
        max_context_tokens: int = 32000,
        history_file: Optional[Path] = None,
        session_dir: Optional[Path] = None
    ):
        """
        Initialize HistoryManager.

        Args:
            max_commands: Maximum commands to keep in history
            max_context: Maximum context messages to keep
            max_context_tokens: Maximum tokens for context window
            history_file: Path to history file. Defaults to ~/.jdev_tui_history
            session_dir: Directory for sessions. Defaults to ~/.juancs/sessions
        """
        self.max_commands = max_commands
        self.max_context = max_context
        self.max_context_tokens = max_context_tokens
        self.commands: List[str] = []
        self.context: List[Dict[str, str]] = []
        self._checkpoints: List[Dict[str, Any]] = []

        # Token tracking for compaction
        self._token_count = 0
        self._compaction_count = 0

        # Configurable paths
        self._history_file = history_file or (Path.home() / ".jdev_tui_history")
        self._session_dir = session_dir or (Path.home() / ".juancs" / "sessions")

        self._load_history()

    # =========================================================================
    # COMMAND HISTORY
    # =========================================================================

    def _load_history(self) -> None:
        """Load history from file."""
        try:
            if self._history_file.exists():
                lines = self._history_file.read_text().strip().split("\n")
                self.commands = lines[-self.max_commands:]
        except Exception as e:
            logger.debug(f"Failed to load history: {e}")

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            self._history_file.write_text("\n".join(self.commands[-self.max_commands:]))
        except Exception as e:
            logger.debug(f"Failed to save history: {e}")

    def add_command(self, command: str) -> None:
        """
        Add command to history.

        Skips duplicate of last command.
        """
        if command and (not self.commands or command != self.commands[-1]):
            self.commands.append(command)
            self._save_history()

    def search_history(self, query: str, limit: int = 10) -> List[str]:
        """
        Search command history.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum results to return

        Returns:
            List of matching commands (most recent first)
        """
        if not query:
            return self.commands[-limit:]

        results = []
        query_lower = query.lower()

        for cmd in reversed(self.commands):
            if query_lower in cmd.lower():
                results.append(cmd)
                if len(results) >= limit:
                    break

        return results

    def get_recent(self, count: int = 10) -> List[str]:
        """Get recent commands."""
        return self.commands[-count:]

    def clear_history(self) -> None:
        """Clear command history."""
        self.commands.clear()
        self._save_history()

    # =========================================================================
    # CONVERSATION CONTEXT
    # =========================================================================

    def add_context(self, role: str, content: str) -> None:
        """
        Add message to conversation context.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.context.append({"role": role, "content": content})
        # Keep context within limits
        if len(self.context) > self.max_context:
            self.context = self.context[-self.max_context:]

    def get_context(self) -> List[Dict[str, str]]:
        """Get conversation context for LLM."""
        return self.context.copy()

    def clear_context(self) -> None:
        """Clear conversation context."""
        self.context.clear()

    # =========================================================================
    # SESSION PERSISTENCE (Claude Code Parity - /resume, /save)
    # =========================================================================

    def save_session(self, session_id: Optional[str] = None) -> str:
        """
        Save current session to disk.

        Args:
            session_id: Optional session identifier. Auto-generated if not provided.

        Returns:
            The session_id used for saving.
        """
        self._session_dir.mkdir(parents=True, exist_ok=True)

        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        session_file = self._session_dir / f"{session_id}.json"

        session_data = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "context": self.context,
            "commands": self.commands[-100:],  # Last 100 commands
            "version": "1.0"
        }

        session_file.write_text(json.dumps(session_data, indent=2, ensure_ascii=False))
        logger.info(f"Session saved: {session_id}")
        return session_id

    def load_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a session from disk.

        Args:
            session_id: Session to load. If None, loads most recent.

        Returns:
            Dictionary with session info (session_id, timestamp, message_count)

        Raises:
            ValueError: If no sessions found or session doesn't exist
        """
        if not self._session_dir.exists():
            raise ValueError("No sessions found")

        if session_id:
            session_file = self._session_dir / f"{session_id}.json"
            if not session_file.exists():
                raise ValueError(f"Session not found: {session_id}")
        else:
            # Get most recent session
            sessions = sorted(
                self._session_dir.glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if not sessions:
                raise ValueError("No sessions found")
            session_file = sessions[0]

        data = json.loads(session_file.read_text())
        self.context = data.get("context", [])
        self.commands = data.get("commands", [])

        logger.info(f"Session loaded: {data.get('session_id')}")
        return {
            "session_id": data.get("session_id"),
            "timestamp": data.get("timestamp"),
            "message_count": len(self.context)
        }

    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List available sessions.

        Args:
            limit: Maximum sessions to return

        Returns:
            List of session info dictionaries
        """
        if not self._session_dir.exists():
            return []

        sessions = sorted(
            self._session_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        result = []

        for session_file in sessions[:limit]:
            try:
                data = json.loads(session_file.read_text())
                result.append({
                    "session_id": data.get("session_id", session_file.stem),
                    "timestamp": data.get("timestamp"),
                    "message_count": len(data.get("context", [])),
                    "file": str(session_file)
                })
            except Exception:
                pass

        return result

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session to delete

        Returns:
            True if deleted, False if not found
        """
        session_file = self._session_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            logger.info(f"Session deleted: {session_id}")
            return True
        return False

    # =========================================================================
    # CHECKPOINT SYSTEM (Claude Code Parity - /rewind)
    # =========================================================================

    def create_checkpoint(self, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a checkpoint of current conversation state.

        Used for /rewind functionality.

        Note: Limited to MAX_CHECKPOINTS (20) to prevent memory leak.
              Oldest checkpoints are removed when limit is reached.

        Args:
            label: Optional label for checkpoint

        Returns:
            Checkpoint info dictionary
        """
        checkpoint = {
            "index": len(self._checkpoints),
            "label": label or f"Checkpoint {len(self._checkpoints) + 1}",
            "timestamp": datetime.now().isoformat(),
            "context": self.context.copy(),
            "message_count": len(self.context)
        }

        self._checkpoints.append(checkpoint)

        # AIR GAP FIX: Limit checkpoint count to prevent memory leak
        if len(self._checkpoints) > self.MAX_CHECKPOINTS:
            # Remove oldest checkpoints, keeping most recent
            self._checkpoints = self._checkpoints[-self.MAX_CHECKPOINTS:]
            # Re-index remaining checkpoints
            for i, cp in enumerate(self._checkpoints):
                cp["index"] = i

        return {
            "index": checkpoint["index"],
            "label": checkpoint["label"],
            "timestamp": checkpoint["timestamp"],
            "message_count": checkpoint["message_count"]
        }

    def get_checkpoints(self) -> List[Dict[str, Any]]:
        """
        Get all checkpoints for current session.

        Returns:
            List of checkpoint info (without full context data)
        """
        return [
            {
                "index": cp["index"],
                "label": cp["label"],
                "timestamp": cp["timestamp"],
                "message_count": cp["message_count"]
            }
            for cp in self._checkpoints
        ]

    def rewind_to_checkpoint(self, index: int) -> Dict[str, Any]:
        """
        Rewind conversation to a specific checkpoint.

        Args:
            index: Checkpoint index to rewind to

        Returns:
            Success info dictionary

        Raises:
            ValueError: If no checkpoints or invalid index
        """
        if not self._checkpoints:
            raise ValueError("No checkpoints available")

        if not 0 <= index < len(self._checkpoints):
            raise ValueError(
                f"Invalid checkpoint index: {index}. Available: 0-{len(self._checkpoints)-1}"
            )

        checkpoint = self._checkpoints[index]
        self.context = checkpoint["context"].copy()

        return {
            "success": True,
            "rewound_to": checkpoint["label"],
            "message_count": len(self.context)
        }

    def clear_checkpoints(self) -> None:
        """Clear all checkpoints."""
        self._checkpoints.clear()

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get history statistics.

        Returns:
            Statistics dictionary
        """
        token_stats = self.estimate_tokens()
        return {
            "command_count": len(self.commands),
            "context_count": len(self.context),
            "checkpoint_count": len(self._checkpoints),
            "max_commands": self.max_commands,
            "max_context": self.max_context,
            "max_checkpoints": self.MAX_CHECKPOINTS,
            "session_dir": str(self._session_dir),
            "history_file": str(self._history_file),
            # Token tracking
            "estimated_tokens": token_stats["estimated_tokens"],
            "max_tokens": self.max_context_tokens,
            "utilization_percent": token_stats["utilization_percent"],
            "compaction_count": self._compaction_count,
        }

    # =========================================================================
    # CONTEXT COMPACTION (Claude Code Parity - Nov 2025)
    # =========================================================================

    def estimate_tokens(self) -> Dict[str, Any]:
        """
        Estimate token count for current context.

        Uses character-based heuristic (4 chars ≈ 1 token).

        Returns:
            Token estimation with utilization metrics
        """
        total_chars = sum(len(msg.get("content", "")) for msg in self.context)
        estimated_tokens = total_chars // self.CHARS_PER_TOKEN
        utilization = estimated_tokens / self.max_context_tokens if self.max_context_tokens > 0 else 0

        return {
            "estimated_tokens": estimated_tokens,
            "total_chars": total_chars,
            "max_tokens": self.max_context_tokens,
            "utilization_percent": round(utilization * 100, 1),
            "needs_compaction": utilization > self.COMPACTION_THRESHOLD,
            "messages_count": len(self.context)
        }

    def needs_compaction(self) -> bool:
        """Check if context needs compaction (>60% utilization)."""
        stats = self.estimate_tokens()
        return stats["needs_compaction"]

    def compact(
        self,
        focus: Optional[str] = None,
        preserve_recent: int = 5,
        summary_fn: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Compact conversation context by summarizing older messages.

        Claude Code Pattern:
        - Preserves recent messages (last N)
        - Summarizes older messages into a single context message
        - Optionally focuses summary on specific topic

        Args:
            focus: Optional topic to focus summary on
            preserve_recent: Number of recent messages to keep intact
            summary_fn: Optional async function to generate summary (LLM-based)

        Returns:
            Compaction result with before/after stats
        """
        before_stats = self.estimate_tokens()

        if len(self.context) <= preserve_recent:
            return {
                "success": False,
                "reason": "Not enough context to compact",
                "before": before_stats,
                "after": before_stats
            }

        # Split context
        old_messages = self.context[:-preserve_recent]
        recent_messages = self.context[-preserve_recent:]

        # Generate summary
        if summary_fn:
            # LLM-based summary (async - caller handles)
            summary = summary_fn(old_messages, focus)
        else:
            # Simple rule-based summary
            summary = self._generate_simple_summary(old_messages, focus)

        # Create compacted context
        summary_message = {
            "role": "system",
            "content": f"[Context Summary - {len(old_messages)} messages compacted]\n{summary}"
        }

        self.context = [summary_message] + recent_messages
        self._compaction_count += 1

        after_stats = self.estimate_tokens()

        return {
            "success": True,
            "before": before_stats,
            "after": after_stats,
            "messages_compacted": len(old_messages),
            "messages_preserved": len(recent_messages),
            "tokens_saved": before_stats["estimated_tokens"] - after_stats["estimated_tokens"],
            "focus": focus,
            "compaction_number": self._compaction_count
        }

    def _generate_simple_summary(
        self,
        messages: List[Dict[str, str]],
        focus: Optional[str] = None
    ) -> str:
        """
        Generate a simple rule-based summary of messages.

        This is a fallback when LLM summarization is not available.

        Args:
            messages: Messages to summarize
            focus: Optional topic focus

        Returns:
            Summary string
        """
        # Group by role
        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]

        # Extract key points
        summary_parts = []

        if user_msgs:
            # Summarize user requests
            user_topics = []
            for msg in user_msgs[-5:]:  # Last 5 user messages
                content = msg.get("content", "")[:100]
                if content:
                    user_topics.append(f"- {content}...")
            if user_topics:
                summary_parts.append("User discussed:\n" + "\n".join(user_topics))

        if assistant_msgs:
            # Count tool usage patterns
            tool_mentions = {}
            for msg in assistant_msgs:
                content = msg.get("content", "")
                for tool in ["read_file", "write_file", "edit_file", "bash_command", "search_files"]:
                    if tool in content.lower():
                        tool_mentions[tool] = tool_mentions.get(tool, 0) + 1

            if tool_mentions:
                tools_used = ", ".join(f"{k}({v}x)" for k, v in sorted(tool_mentions.items(), key=lambda x: -x[1])[:5])
                summary_parts.append(f"Tools used: {tools_used}")

        if focus:
            summary_parts.append(f"Focus topic: {focus}")

        return "\n".join(summary_parts) if summary_parts else "Previous conversation context (details compacted)"

    def replace_with_summary(self, summary: str, preserve_recent: int = 5) -> Dict[str, Any]:
        """
        Replace older context with a custom summary.

        Used when LLM generates a better summary externally.

        Args:
            summary: Summary text to use
            preserve_recent: Number of recent messages to keep

        Returns:
            Result dictionary
        """
        before_stats = self.estimate_tokens()

        if len(self.context) <= preserve_recent:
            return {
                "success": False,
                "reason": "Not enough context to compact"
            }

        recent_messages = self.context[-preserve_recent:]
        old_count = len(self.context) - preserve_recent

        summary_message = {
            "role": "system",
            "content": f"[Context Summary - {old_count} messages compacted]\n{summary}"
        }

        self.context = [summary_message] + recent_messages
        self._compaction_count += 1

        after_stats = self.estimate_tokens()

        return {
            "success": True,
            "messages_compacted": old_count,
            "tokens_before": before_stats["estimated_tokens"],
            "tokens_after": after_stats["estimated_tokens"],
            "tokens_saved": before_stats["estimated_tokens"] - after_stats["estimated_tokens"]
        }

    def auto_compact_if_needed(self, preserve_recent: int = 5) -> Optional[Dict[str, Any]]:
        """
        Automatically compact context if utilization exceeds threshold.

        Called after adding context to maintain healthy context window.

        Returns:
            Compaction result if compaction was performed, None otherwise
        """
        if self.needs_compaction():
            return self.compact(preserve_recent=preserve_recent)
        return None
