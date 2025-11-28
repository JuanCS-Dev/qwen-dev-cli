"""
Domain Exceptions.

SCALE & SUSTAIN Phase 1.3 - Type Consolidation.

Author: JuanCS Dev
Date: 2025-11-26
"""


class QwenCoreError(Exception):
    """Base exception for all jdev_core errors."""
    pass


class CapabilityViolationError(QwenCoreError):
    """
    Raised when an agent attempts to use a capability it doesn't have.

    Example:
        if AgentCapability.BASH_EXEC not in agent.capabilities:
            raise CapabilityViolationError(
                agent_id=agent.id,
                capability="BASH_EXEC",
                message="Agent not authorized for command execution"
            )
    """
    def __init__(self, agent_id: str, capability: str, message: str = ""):
        self.agent_id = agent_id
        self.capability = capability
        super().__init__(
            f"Agent '{agent_id}' lacks capability '{capability}'"
            + (f": {message}" if message else "")
        )


class TaskValidationError(QwenCoreError):
    """Raised when task validation fails."""
    pass


class AgentTimeoutError(QwenCoreError):
    """Raised when agent execution times out."""
    pass


__all__ = [
    'QwenCoreError',
    'CapabilityViolationError',
    'TaskValidationError',
    'AgentTimeoutError',
]
