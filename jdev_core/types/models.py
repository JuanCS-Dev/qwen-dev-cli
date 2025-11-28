"""
Domain Models for Agent System.

SCALE & SUSTAIN Phase 1.3 - Type Consolidation.

Migrated from jdev_core/types.py (legacy).

Contains Pydantic models for:
- AgentTask: Task specification
- AgentResponse: Execution response
- TaskResult: Result wrapper

Author: JuanCS Dev
Date: 2025-11-26
"""

import sys
import uuid
import warnings
from datetime import datetime
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field, model_validator

from .agents import TaskStatus


class AgentTask(BaseModel):
    """
    Immutable task specification for agent execution.

    Attributes:
        task_id: Unique identifier (auto-generated UUID)
        request: The task description/prompt
        context: Additional context data (limited to 10MB)
        session_id: Session identifier for multi-turn conversations
        metadata: Arbitrary metadata (limited to 10k keys)
        history: Previous interactions for context
    """
    model_config = {
        "strict": True,
        "validate_assignment": True,
        "frozen": False,  # Allow mutation for history append
    }

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: str = Field(..., max_length=100_000)
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: str = Field(default="default")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def handle_deprecated_description(cls, values: Any) -> Any:
        """Migrate deprecated 'description' field to 'request'."""
        if isinstance(values, dict) and 'description' in values:
            warnings.warn(
                "AgentTask field 'description' is deprecated. Use 'request' instead.",
                DeprecationWarning,
                stacklevel=3
            )
            if 'request' not in values:
                values['request'] = values['description']
            del values['description']
        return values

    @model_validator(mode='after')
    def validate_size_limits(self) -> 'AgentTask':
        """Prevent resource exhaustion attacks."""
        # Context size limit: 10MB
        context_size = sys.getsizeof(str(self.context))
        max_context_size = 10 * 1024 * 1024
        if context_size > max_context_size:
            raise ValueError(
                f"Context size ({context_size:,} bytes) exceeds limit "
                f"({max_context_size:,} bytes)"
            )

        # Key count limit: 10k
        if isinstance(self.context, dict) and len(self.context) > 10_000:
            raise ValueError(
                f"Context has {len(self.context)} keys, maximum is 10000. "
                "This prevents resource exhaustion attacks."
            )

        return self


class AgentResponse(BaseModel):
    """
    Immutable response from agent execution.

    Attributes:
        success: Whether the task completed successfully
        data: Result data from execution
        reasoning: Chain-of-thought explanation
        error: Error message if failed
        metrics: Numeric execution metrics (tokens, time, etc.)
        timestamp: When the response was created

    Properties:
        metadata: Alias for metrics (backward compatibility)
    """
    model_config = {
        "strict": True,
        "validate_assignment": True,
        "frozen": False,  # Allow property access
    }

    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = Field(default="")
    error: Optional[str] = Field(default=None)
    metrics: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def metadata(self) -> Dict[str, float]:
        """Alias for metrics (backward compatibility)."""
        return self.metrics


class TaskResult(BaseModel):
    """
    Result wrapper for task execution.

    Used for compatibility with orchestration systems.
    """
    model_config = {
        "strict": True,
        "frozen": True,
    }

    task_id: str
    status: TaskStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


__all__ = [
    'AgentTask',
    'AgentResponse',
    'TaskResult',
]
