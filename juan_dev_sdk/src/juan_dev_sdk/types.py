"""
SDK Types.

SCALE & SUSTAIN Phase 2.3 - SDK Types.

Public type definitions for SDK users.

Author: JuanCS Dev
Date: 2025-11-26
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class MessageRole(Enum):
    """Message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """Chat message."""
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def user(cls, content: str) -> 'Message':
        """Create user message."""
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> 'Message':
        """Create assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content)

    @classmethod
    def system(cls, content: str) -> 'Message':
        """Create system message."""
        return cls(role=MessageRole.SYSTEM, content=content)


@dataclass
class ToolCall:
    """Tool call request."""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: Optional[str] = None


@dataclass
class ToolResult:
    """Tool execution result."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class AgentResponse:
    """Response from agent execution."""
    content: str
    agent_name: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SDKConfig:
    """SDK configuration."""
    api_key: Optional[str] = None
    base_url: str = "http://localhost:8080"
    timeout: float = 60.0
    max_retries: int = 3
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'SDKConfig':
        """Create config from environment variables."""
        import os
        return cls(
            api_key=os.getenv("JUAN_DEV_API_KEY"),
            base_url=os.getenv("JUAN_DEV_URL", "http://localhost:8080"),
        )


__all__ = [
    'Message',
    'MessageRole',
    'ToolCall',
    'ToolResult',
    'AgentResponse',
    'SDKConfig',
]
