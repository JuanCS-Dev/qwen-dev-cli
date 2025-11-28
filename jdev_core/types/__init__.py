"""
Unified Type System for JDev.

SCALE & SUSTAIN Phase 1.3 - Type Consolidation.

This package provides canonical type definitions for the entire codebase.
Import from here instead of duplicating types.

Usage:
    from jdev_core.types import CircuitState, CircuitBreaker
    from jdev_core.types import AgentRole, AgentIdentity
    from jdev_core.types import BlockType, BlockInfo
    from jdev_core.types import AgentTask, AgentResponse

Author: JuanCS Dev
Date: 2025-11-26
"""

# Circuit Breaker Pattern
from .circuit import (
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerStats,
    CircuitBreaker,
    SimpleCircuitBreaker,
)

# Block/Markdown Types
from .blocks import (
    BlockType,
    BlockInfo,
    BlockRenderConfig,
)

# Agent Types
from .agents import (
    AgentRole,
    AgentPriority,
    AgentCapability,
    AgentIdentity,
    TaskStatus,
    PlanningMode,
    ConfidenceLevel,
)

# Planner Types
from .planner import (
    ExecutionStrategy,
    CheckpointType,
    DependencyType,
    StepConfidence,
    Checkpoint,
)

# Domain Models (Pydantic)
from .models import (
    AgentTask,
    AgentResponse,
    TaskResult,
)

# Exceptions
from .exceptions import (
    QwenCoreError,
    CapabilityViolationError,
    TaskValidationError,
    AgentTimeoutError,
)


__all__ = [
    # Circuit
    'CircuitState',
    'CircuitBreakerConfig',
    'CircuitBreakerStats',
    'CircuitBreaker',
    'SimpleCircuitBreaker',
    # Blocks
    'BlockType',
    'BlockInfo',
    'BlockRenderConfig',
    # Agents
    'AgentRole',
    'AgentPriority',
    'AgentCapability',
    'AgentIdentity',
    'TaskStatus',
    'PlanningMode',
    'ConfidenceLevel',
    # Planner
    'ExecutionStrategy',
    'CheckpointType',
    'DependencyType',
    'StepConfidence',
    'Checkpoint',
    # Models
    'AgentTask',
    'AgentResponse',
    'TaskResult',
    # Exceptions
    'QwenCoreError',
    'CapabilityViolationError',
    'TaskValidationError',
    'AgentTimeoutError',
]
