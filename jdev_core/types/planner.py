"""
Unified Planner Types.

SCALE & SUSTAIN Phase 1.3 - Type Consolidation.

Consolidated from:
- jdev_cli/agents/planner/types.py (ExecutionStrategy, CheckpointType, etc.)

Author: JuanCS Dev
Date: 2025-11-26
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional


class ExecutionStrategy(str, Enum):
    """Execution patterns for multi-agent coordination."""
    SEQUENTIAL = "sequential"      # One after another (dependencies)
    PARALLEL = "parallel"          # All at once (no dependencies)
    FORK_JOIN = "fork-join"        # Parallel + merge at end
    PIPELINE = "pipeline"          # Stream output between agents
    CONDITIONAL = "conditional"    # Based on runtime conditions


class CheckpointType(str, Enum):
    """Types of execution checkpoints."""
    VALIDATION = "validation"      # Validate before continuing
    ROLLBACK = "rollback"          # Can rollback to here
    DECISION = "decision"          # Decision point for branching


class DependencyType(str, Enum):
    """Types of dependencies between steps."""
    HARD = "hard"            # Must complete before next
    SOFT = "soft"            # Preferred but not required
    DATA = "data"            # Needs data from previous
    RESOURCE = "resource"    # Shared resource lock


@dataclass
class StepConfidence:
    """Confidence rating for a planning step."""
    score: float  # 0.0 to 1.0
    reasoning: str = ""
    risk_factors: List[str] = field(default_factory=list)

    @property
    def level(self) -> str:
        """Get confidence level string."""
        if self.score >= 0.9:
            return "certain"
        elif self.score >= 0.7:
            return "confident"
        elif self.score >= 0.5:
            return "moderate"
        elif self.score >= 0.3:
            return "low"
        return "speculative"


@dataclass
class Checkpoint:
    """Execution checkpoint for rollback/validation."""
    checkpoint_id: str
    checkpoint_type: CheckpointType
    step_index: int
    state_snapshot: Optional[dict] = None
    validation_criteria: Optional[str] = None


__all__ = [
    'ExecutionStrategy',
    'CheckpointType',
    'DependencyType',
    'StepConfidence',
    'Checkpoint',
]
