"""
TodoManager - TODO List Management.

Extracted from Bridge as part of SCALE & SUSTAIN Phase 1.1.

Thread-safe TODO management with:
- Add/update/clear operations
- Status tracking (done/pending)
- Thread-safe list implementation

Author: JuanCS Dev
Date: 2025-11-26
"""

from typing import Any, Dict, List

from jdev_tui.core.interfaces import ITodoManager
from jdev_tui.core.resilience import ThreadSafeList


class TodoManager(ITodoManager):
    """
    Thread-safe TODO list manager.

    Implements ITodoManager interface for:
    - Managing TODO items
    - Tracking completion status
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize TodoManager with thread-safe list."""
        self._todos: ThreadSafeList[Dict[str, Any]] = ThreadSafeList()

    def get_todos(self) -> List[Dict[str, Any]]:
        """
        Get all TODO items (thread-safe copy).

        Returns:
            List of TODO items with 'text' and 'done' fields.
        """
        return self._todos.copy()

    def add_todo(self, text: str) -> None:
        """
        Add a new TODO item (thread-safe).

        Args:
            text: The TODO item text.
        """
        self._todos.append({"text": text, "done": False})

    def update_todo(self, index: int, done: bool) -> bool:
        """
        Update TODO status (thread-safe).

        Args:
            index: Index of the TODO item.
            done: New completion status.

        Returns:
            True if updated successfully, False otherwise.
        """
        todos = self._todos.copy()
        if 0 <= index < len(todos):
            todos[index]["done"] = done
            # Replace entire list (atomic operation)
            self._todos.clear()
            for todo in todos:
                self._todos.append(todo)
            return True
        return False

    def clear_todos(self) -> None:
        """Clear all TODO items (thread-safe)."""
        self._todos.clear()

    def get_pending_count(self) -> int:
        """Get count of pending (not done) TODOs."""
        return sum(1 for todo in self._todos.copy() if not todo.get("done", False))

    def get_completed_count(self) -> int:
        """Get count of completed TODOs."""
        return sum(1 for todo in self._todos.copy() if todo.get("done", False))

    def get_stats(self) -> Dict[str, int]:
        """Get TODO statistics."""
        todos = self._todos.copy()
        pending = sum(1 for t in todos if not t.get("done", False))
        completed = sum(1 for t in todos if t.get("done", False))
        return {
            "total": len(todos),
            "pending": pending,
            "completed": completed
        }
