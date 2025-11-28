"""
ContextManager - Conversation Context Management.

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Manages:
- Conversation context (messages)
- Token statistics
- Context compaction

Author: JuanCS Dev
Date: 2025-11-26
"""

from typing import Any, Callable, Dict, List, Optional

from jdev_tui.core.interfaces import IContextManager


class ContextManager(IContextManager):
    """
    Conversation context manager.

    Implements IContextManager interface for:
    - Managing conversation messages
    - Token usage tracking
    - Context compaction for long conversations (Claude Code Parity)
    """

    # Default context window size
    MAX_CONTEXT_MESSAGES = 50
    MAX_CONTEXT_TOKENS = 32000  # Claude Code parity
    COMPACT_THRESHOLD = 0.60    # Trigger at 60% utilization
    COMPACT_KEEP_FIRST = 2
    COMPACT_KEEP_LAST = 8
    CHARS_PER_TOKEN = 4         # Rough estimation

    def __init__(
        self,
        context_getter: Optional[Callable[[], List[Dict[str, Any]]]] = None,
        context_setter: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ):
        """
        Initialize ContextManager.

        Args:
            context_getter: Callable to get context from external source.
            context_setter: Callable to set context in external source.
        """
        self._internal_context: List[Dict[str, Any]] = []
        self._context_getter = context_getter
        self._context_setter = context_setter
        self._session_tokens = 0

    @property
    def _context(self) -> List[Dict[str, Any]]:
        """Get context from external source or internal storage."""
        if self._context_getter:
            return self._context_getter()
        return self._internal_context

    @_context.setter
    def _context(self, value: List[Dict[str, Any]]) -> None:
        """Set context in external source or internal storage."""
        if self._context_setter:
            self._context_setter(value)
        else:
            self._internal_context = value

    def get_context(self) -> List[Dict[str, Any]]:
        """
        Get current conversation context.

        Returns:
            List of context messages.
        """
        return list(self._context)

    def add_context(self, role: str, content: str) -> None:
        """
        Add message to context.

        Args:
            role: Message role (user, assistant, system).
            content: Message content.
        """
        ctx = self._context
        ctx.append({"role": role, "content": content})

        # Update token estimate
        self._session_tokens += len(content) // 4

        # Auto-compact if too large
        if len(ctx) > self.MAX_CONTEXT_MESSAGES:
            self._auto_compact()

        self._context = ctx

    def clear_context(self) -> None:
        """Clear conversation context."""
        self._context = []

    def compact_context(self, focus: Optional[str] = None) -> Dict[str, Any]:
        """
        Compact conversation context with intelligent summarization.

        Claude Code Parity Pattern:
        - Preserves system context (first N messages)
        - Preserves recent messages (last M messages)
        - Summarizes middle messages into a context summary
        - Optionally focuses summary on specific topic

        Args:
            focus: Optional topic to focus on during compaction.

        Returns:
            Dictionary with compaction stats.
        """
        ctx = self._context
        before_count = len(ctx)
        before_tokens = self._estimate_tokens(ctx)

        # Not enough to compact
        if len(ctx) <= (self.COMPACT_KEEP_FIRST + self.COMPACT_KEEP_LAST):
            return {
                "success": False,
                "reason": "Not enough messages to compact",
                "before_messages": before_count,
                "before_tokens": before_tokens,
                "after_messages": before_count,
                "after_tokens": before_tokens,
                "tokens_saved": 0
            }

        # Split context
        first_msgs = ctx[:self.COMPACT_KEEP_FIRST]
        middle_msgs = ctx[self.COMPACT_KEEP_FIRST:-self.COMPACT_KEEP_LAST]
        last_msgs = ctx[-self.COMPACT_KEEP_LAST:]

        # Generate summary of middle messages
        summary = self._generate_summary(middle_msgs, focus)

        # Create summary message
        summary_message = {
            "role": "system",
            "content": f"[Context Summary - {len(middle_msgs)} messages compacted]\n{summary}"
        }

        # Rebuild context
        new_ctx = first_msgs + [summary_message] + last_msgs
        self._context = new_ctx

        after_count = len(new_ctx)
        after_tokens = self._estimate_tokens(new_ctx)

        return {
            "success": True,
            "before_messages": before_count,
            "before_tokens": before_tokens,
            "after_messages": after_count,
            "after_tokens": after_tokens,
            "tokens_saved": before_tokens - after_tokens,
            "messages_compacted": len(middle_msgs),
            "focus": focus
        }

    def _generate_summary(
        self,
        messages: List[Dict[str, Any]],
        focus: Optional[str] = None
    ) -> str:
        """
        Generate a summary of messages for compaction.

        Args:
            messages: Messages to summarize.
            focus: Optional topic to focus on.

        Returns:
            Summary string.
        """
        if not messages:
            return "No previous context."

        # Collect stats
        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]

        summary_parts = []

        # Summarize user topics
        if user_msgs:
            topics = []
            for msg in user_msgs[-5:]:  # Last 5 user messages
                content = str(msg.get("content", ""))[:80]
                if content:
                    topics.append(f"- {content}...")
            if topics:
                summary_parts.append("User discussed:\n" + "\n".join(topics))

        # Track tools used
        if assistant_msgs:
            tool_counts: Dict[str, int] = {}
            for msg in assistant_msgs:
                content = str(msg.get("content", ""))
                for tool in ["read_file", "write_file", "edit_file", "bash_command", "search_files", "git_status"]:
                    if tool in content.lower():
                        tool_counts[tool] = tool_counts.get(tool, 0) + 1

            if tool_counts:
                tools_str = ", ".join(
                    f"{k}({v}x)"
                    for k, v in sorted(tool_counts.items(), key=lambda x: -x[1])[:5]
                )
                summary_parts.append(f"Tools used: {tools_str}")

        # Add focus if provided
        if focus:
            summary_parts.append(f"Focus: {focus}")

        return "\n".join(summary_parts) if summary_parts else "Previous conversation context (compacted)"

    def _estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Estimate token count for messages."""
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        return total_chars // self.CHARS_PER_TOKEN

    def needs_compaction(self) -> bool:
        """Check if context needs compaction (>60% utilization)."""
        tokens = self._estimate_tokens(self._context)
        utilization = tokens / self.MAX_CONTEXT_TOKENS if self.MAX_CONTEXT_TOKENS > 0 else 0
        return utilization > self.COMPACT_THRESHOLD

    def auto_compact_if_needed(self) -> Optional[Dict[str, Any]]:
        """
        Automatically compact if utilization exceeds threshold.

        Returns:
            Compaction result if performed, None otherwise.
        """
        if self.needs_compaction():
            return self.compact_context()
        return None

    def _auto_compact(self) -> None:
        """Automatically compact when context is too large."""
        ctx = self._context
        if len(ctx) > self.MAX_CONTEXT_MESSAGES:
            # Keep more context during auto-compact
            keep_last = min(20, len(ctx) - self.COMPACT_KEEP_FIRST)
            ctx = ctx[:self.COMPACT_KEEP_FIRST] + ctx[-keep_last:]
            self._context = ctx

    def get_token_stats(self) -> Dict[str, Any]:
        """
        Get token usage statistics.

        Returns:
            Dictionary with token statistics.
        """
        context_size = sum(len(str(m.get("content", ""))) for m in self._context)
        context_tokens = context_size // 4  # Rough estimate

        return {
            "session_tokens": self._session_tokens,
            "total_tokens": self._session_tokens,
            "input_tokens": int(self._session_tokens * 0.6),
            "output_tokens": int(self._session_tokens * 0.4),
            "context_tokens": context_tokens,
            "context_messages": len(self._context),
            "max_tokens": 128000,
            "cost": self._session_tokens * 0.000001  # Rough Gemini pricing
        }

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context state."""
        ctx = self._context
        return {
            "message_count": len(ctx),
            "user_messages": sum(1 for m in ctx if m.get("role") == "user"),
            "assistant_messages": sum(1 for m in ctx if m.get("role") == "assistant"),
            "system_messages": sum(1 for m in ctx if m.get("role") == "system"),
            "total_chars": sum(len(str(m.get("content", ""))) for m in ctx)
        }

    def add_session_tokens(self, tokens: int) -> None:
        """Add to session token count."""
        self._session_tokens += tokens

    def reset_session_tokens(self) -> None:
        """Reset session token count."""
        self._session_tokens = 0
