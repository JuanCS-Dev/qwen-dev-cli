"""
planner: Goal-Oriented Action Planning System.

This package provides a comprehensive planning system based on:
- GOAP (Goal-Oriented Action Planning) from F.E.A.R.
- Claude Code Plan Mode patterns
- Cursor 2.1 Clarifying Questions
- Devin Confidence Ratings
- Verbalized Sampling (Zhang et al. 2025)

Modules:
- agent: The main PlannerAgent class
- types: Domain types (Enums, Pydantic models)
- goap: GOAP planning with A* pathfinding
- dependency: Dependency graph analysis
- validation: Plan validation and monitoring

Example:
    from qwen_dev_cli.agents.planner import PlannerAgent
    # or
    from qwen_dev_cli.agents.planner.types import ExecutionPlan, SOPStep
    from qwen_dev_cli.agents.planner.goap import GOAPPlanner, WorldState
"""

# Re-export types
from .types import (
    # Enums
    ExecutionStrategy,
    AgentPriority,
    CheckpointType,
    PlanningMode,
    ConfidenceLevel,
    PlanStrategy,
    # Dataclasses
    StepConfidence,
    PlanProbabilities,
    # Pydantic Models
    ClarifyingQuestion,
    ClarificationResponse,
    AlternativePlan,
    MultiPlanResult,
    SOPStep,
    ExecutionStage,
    ExecutionPlan,
)

# Re-export GOAP
from .goap import (
    WorldState,
    GoalState,
    Action,
    GOAPPlanner,
)

# Re-export dependency analysis
from .dependency import DependencyAnalyzer

# Re-export validation
from .validation import (
    PlanValidator,
    ExecutionEvent,
    ExecutionMonitor,
)

# Re-export PlannerAgent from agent module
from .agent import PlannerAgent

__all__ = [
    # Main Agent
    "PlannerAgent",
    # Types - Enums
    "ExecutionStrategy",
    "AgentPriority",
    "CheckpointType",
    "PlanningMode",
    "ConfidenceLevel",
    "PlanStrategy",
    # Types - Dataclasses
    "StepConfidence",
    "PlanProbabilities",
    # Types - Pydantic
    "ClarifyingQuestion",
    "ClarificationResponse",
    "AlternativePlan",
    "MultiPlanResult",
    "SOPStep",
    "ExecutionStage",
    "ExecutionPlan",
    # GOAP
    "WorldState",
    "GoalState",
    "Action",
    "GOAPPlanner",
    # Dependency
    "DependencyAnalyzer",
    # Validation
    "PlanValidator",
    "ExecutionEvent",
    "ExecutionMonitor",
]
