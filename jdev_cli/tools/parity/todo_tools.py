"""
Todo Tools - TodoRead, TodoWrite
================================

Task management tools for Claude Code parity.

Contains:
- TodoReadTool: Get current todo list
- TodoWriteTool: Manage todo list (add, update, complete)

Author: JuanCS Dev
Date: 2025-11-27
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict, List

from jdev_cli.tools.base import Tool, ToolCategory, ToolResult

logger = logging.getLogger(__name__)


# =============================================================================
# SHARED TODO STATE (Thread-Safe Singleton)
# =============================================================================

class TodoState:
    """
    Thread-safe singleton for shared todo state.

    Ensures TodoRead and TodoWrite share the same list.
    """

    _instance: 'TodoState' = None
    _lock = threading.RLock()

    def __new__(cls) -> 'TodoState':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._todos: List[Dict[str, Any]] = []
        return cls._instance

    @property
    def todos(self) -> List[Dict[str, Any]]:
        """Get the current todo list (copy for safety)."""
        with self._lock:
            return list(self._todos)

    @todos.setter
    def todos(self, value: List[Dict[str, Any]]) -> None:
        """Set the todo list."""
        with self._lock:
            self._todos = list(value) if value else []

    def count(self) -> int:
        """Get todo count."""
        with self._lock:
            return len(self._todos)

    def count_by_status(self) -> Dict[str, int]:
        """Get counts by status."""
        with self._lock:
            counts = {"pending": 0, "in_progress": 0, "completed": 0}
            for todo in self._todos:
                status = todo.get("status", "pending")
                if status in counts:
                    counts[status] += 1
            return counts

    def clear(self) -> None:
        """Clear all todos (for testing)."""
        with self._lock:
            self._todos.clear()


# Global state instance
_todo_state = TodoState()


# =============================================================================
# TODO READ TOOL
# =============================================================================

class TodoReadTool(Tool):
    """
    Read current todo list.

    Claude Code parity: Access the current task list for visibility.

    Example:
        result = await todo_read.execute()
        todos = result.data  # List of todo items
    """

    def __init__(self):
        super().__init__()
        self.name = "todo_read"
        self.category = ToolCategory.CONTEXT
        self.description = "Get current todo list"
        self.parameters = {}

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Get todos."""
        todos = _todo_state.todos
        counts = _todo_state.count_by_status()

        return ToolResult(
            success=True,
            data=todos,
            metadata={
                "count": len(todos),
                "pending": counts["pending"],
                "in_progress": counts["in_progress"],
                "completed": counts["completed"]
            }
        )


# =============================================================================
# TODO WRITE TOOL
# =============================================================================

class TodoWriteTool(Tool):
    """
    Manage todo list - add, update, complete tasks.

    Claude Code parity: Full todo management with status tracking.

    Todo item schema:
    - content: Task description (imperative form)
    - status: "pending" | "in_progress" | "completed"
    - activeForm: Present continuous form (e.g., "Running tests")

    Example:
        result = await todo_write.execute(todos=[
            {"content": "Fix bug", "status": "in_progress", "activeForm": "Fixing bug"},
            {"content": "Write tests", "status": "pending", "activeForm": "Writing tests"},
        ])
    """

    # Valid status values
    VALID_STATUSES = {"pending", "in_progress", "completed"}

    def __init__(self):
        super().__init__()
        self.name = "todo_write"
        self.category = ToolCategory.CONTEXT
        self.description = "Manage todo list (add, update, complete tasks)"
        self.parameters = {
            "todos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed"]
                        },
                        "activeForm": {"type": "string"}
                    }
                },
                "description": "Updated todo list",
                "required": True
            }
        }

    async def _execute_validated(self, **kwargs) -> ToolResult:
        """Update todos."""
        todos = kwargs.get("todos", [])

        # Validate input
        if not isinstance(todos, list):
            return ToolResult(success=False, error="todos must be an array")

        # Validate and normalize each todo
        validated_todos = []
        errors = []

        for i, todo in enumerate(todos):
            if not isinstance(todo, dict):
                errors.append(f"Item {i}: must be an object")
                continue

            content = todo.get("content", "")
            status = todo.get("status", "pending")
            active_form = todo.get("activeForm", "")

            # Validate content
            if not content:
                errors.append(f"Item {i}: content is required")
                continue

            # Validate status
            if status not in self.VALID_STATUSES:
                logger.warning(f"Invalid status '{status}' at item {i}, defaulting to 'pending'")
                status = "pending"

            # Generate activeForm if missing
            if not active_form:
                # Simple heuristic: add "ing" to verb
                active_form = self._generate_active_form(content)

            validated_todos.append({
                "content": str(content)[:500],  # Limit length
                "status": status,
                "activeForm": str(active_form)[:500]
            })

        if errors:
            return ToolResult(
                success=False,
                error=f"Validation errors: {'; '.join(errors)}"
            )

        # Update shared state
        _todo_state.todos = validated_todos
        counts = _todo_state.count_by_status()

        return ToolResult(
            success=True,
            data={
                "updated": len(validated_todos),
                "counts": counts
            },
            metadata={
                "todos": validated_todos,
                "total": len(validated_todos)
            }
        )

    def _generate_active_form(self, content: str) -> str:
        """Generate active form from content if not provided."""
        if not content:
            return ""

        # If already starts with gerund-like word, use as-is
        if content.split()[0].endswith("ing"):
            return content

        # Simple transformation: capitalize first word
        words = content.split()
        if words:
            # Common verb mappings
            verb_map = {
                "fix": "Fixing",
                "add": "Adding",
                "update": "Updating",
                "remove": "Removing",
                "delete": "Deleting",
                "create": "Creating",
                "write": "Writing",
                "read": "Reading",
                "run": "Running",
                "test": "Testing",
                "build": "Building",
                "deploy": "Deploying",
                "implement": "Implementing",
                "refactor": "Refactoring",
                "review": "Reviewing",
                "merge": "Merging",
                "configure": "Configuring",
                "install": "Installing",
                "setup": "Setting up",
            }

            first_word = words[0].lower()
            if first_word in verb_map:
                words[0] = verb_map[first_word]
            else:
                # Default: capitalize
                words[0] = words[0].capitalize()

            return " ".join(words)

        return content


# =============================================================================
# REGISTRY HELPER
# =============================================================================

def get_todo_tools() -> List[Tool]:
    """Get all todo management tools."""
    return [
        TodoReadTool(),
        TodoWriteTool(),
    ]


# For testing - allow clearing state
def clear_todo_state() -> None:
    """Clear todo state (for testing)."""
    _todo_state.clear()


__all__ = [
    "TodoReadTool",
    "TodoWriteTool",
    "TodoState",
    "get_todo_tools",
    "clear_todo_state",
]
