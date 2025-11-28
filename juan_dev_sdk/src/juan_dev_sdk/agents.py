"""
Agent Builder.

SCALE & SUSTAIN Phase 2.3 - SDK Agent Creation.

Helpers for creating custom agents.

Author: JuanCS Dev
Date: 2025-11-26
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional, AsyncIterator


@dataclass
class AgentConfig:
    """Agent configuration."""
    name: str
    description: str
    system_prompt: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentBuilder:
    """
    Builder for creating custom agents.

    Usage:
        agent = (AgentBuilder("my-agent")
            .description("A custom agent")
            .system_prompt("You are a helpful assistant")
            .capability("code_review")
            .on_execute(my_execute_fn)
            .build())
    """

    def __init__(self, name: str):
        """Initialize builder with agent name."""
        self._config = AgentConfig(name=name, description="")
        self._execute_fn: Optional[Callable] = None

    def description(self, desc: str) -> 'AgentBuilder':
        """Set agent description."""
        self._config.description = desc
        return self

    def system_prompt(self, prompt: str) -> 'AgentBuilder':
        """Set system prompt."""
        self._config.system_prompt = prompt
        return self

    def capability(self, cap: str) -> 'AgentBuilder':
        """Add a capability."""
        self._config.capabilities.append(cap)
        return self

    def capabilities(self, caps: List[str]) -> 'AgentBuilder':
        """Set capabilities list."""
        self._config.capabilities = caps
        return self

    def metadata(self, **kwargs) -> 'AgentBuilder':
        """Add metadata."""
        self._config.metadata.update(kwargs)
        return self

    def on_execute(self, fn: Callable) -> 'AgentBuilder':
        """Set execute handler."""
        self._execute_fn = fn
        return self

    def build(self) -> 'CustomAgent':
        """Build the agent."""
        if not self._config.description:
            raise ValueError("Agent description is required")
        return CustomAgent(self._config, self._execute_fn)


class CustomAgent:
    """Custom agent created via builder."""

    def __init__(
        self,
        config: AgentConfig,
        execute_fn: Optional[Callable] = None
    ):
        self.config = config
        self._execute_fn = execute_fn

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description

    async def execute(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Execute agent."""
        if self._execute_fn:
            result = self._execute_fn(message, context)
            if hasattr(result, '__aiter__'):
                async for chunk in result:
                    yield chunk
            else:
                yield {"type": "result", "data": result}
        else:
            yield {"type": "result", "data": f"Agent {self.name} executed"}


def create_agent(
    name: str,
    description: str,
    system_prompt: Optional[str] = None,
    execute_fn: Optional[Callable] = None,
) -> CustomAgent:
    """
    Create a custom agent.

    Shorthand for AgentBuilder.

    Args:
        name: Agent name
        description: Agent description
        system_prompt: Optional system prompt
        execute_fn: Optional execute handler

    Returns:
        Custom agent instance
    """
    builder = (AgentBuilder(name)
        .description(description))

    if system_prompt:
        builder.system_prompt(system_prompt)

    if execute_fn:
        builder.on_execute(execute_fn)

    return builder.build()


__all__ = ['AgentBuilder', 'CustomAgent', 'AgentConfig', 'create_agent']
