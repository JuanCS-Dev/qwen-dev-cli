"""
Unified Agent Types.

SCALE & SUSTAIN Phase 1.3 - Type Consolidation.

Consolidated from:
- jdev_core/types.py:51 (AgentRole - comprehensive)
- jdev_cli/agents/protocol.py:52 (AgentRole - basic)
- jdev_cli/agents/protocol.py:149 (AgentIdentity)
- jdev_cli/core/agent_identity.py:71 (AgentIdentity - deprecated)
- jdev_cli/agents/planner/types.py:43 (AgentPriority)

Author: JuanCS Dev
Date: 2025-11-26
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Set, Dict, Any, Optional


class AgentRole(str, Enum):
    """
    Unified agent role types in the system.

    Core Roles:
        ARCHITECT: System architecture and design decisions
        EXPLORER: Codebase exploration and understanding
        PLANNER: Task planning and coordination
        REFACTORER: Code refactoring and improvement
        REVIEWER: Code review and quality assurance
        EXECUTOR: Command execution agent
        DEBUGGER: Debugging and error diagnosis

    Specialized Roles:
        SECURITY: Security analysis and vulnerability detection
        PERFORMANCE: Performance optimization and profiling
        TESTING: Test generation and execution
        DOCUMENTATION: Documentation generation and maintenance
        DATABASE: Database operations and schema management
        DEVOPS: DevOps operations and CI/CD

    Governance Roles:
        GOVERNANCE/JUSTICA: Constitutional governance (Justiça framework)
        COUNSELOR/SOFIA: Wise counselor (Sofia framework)
        MAESTRO: Orchestration coordinator
    """
    # Core roles
    ARCHITECT = "architect"
    EXPLORER = "explorer"
    PLANNER = "planner"
    REFACTORER = "refactorer"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    DEBUGGER = "debugger"

    # Specialized roles
    SECURITY = "security"
    PERFORMANCE = "performance"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DATABASE = "database"
    DEVOPS = "devops"

    # Governance roles
    GOVERNANCE = "governance"
    JUSTICA = "justica"  # Alias for governance
    COUNSELOR = "counselor"
    SOFIA = "sofia"  # Alias for counselor
    MAESTRO = "maestro"

    # Legacy aliases (deprecated)
    REFACTOR = "refactor"  # Use REFACTORER instead


class AgentPriority(str, Enum):
    """Priority levels for agent tasks."""
    CRITICAL = "critical"  # Must complete for success
    HIGH = "high"          # Important but can continue
    MEDIUM = "medium"      # Nice to have
    LOW = "low"            # Optional enhancement


class AgentCapability(str, Enum):
    """
    Capability flags for agent sandboxing.

    Used to restrict what tools an agent can access.
    """
    # Core capabilities (new naming)
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_COMMANDS = "execute_commands"
    GIT_OPERATIONS = "git_operations"
    NETWORK_ACCESS = "network_access"
    SYSTEM_CONFIG = "system_config"

    # Legacy capabilities (used by existing agents - backward compatible)
    READ_ONLY = "read_only"           # Can only read files
    FILE_EDIT = "file_edit"           # Can read and write files
    BASH_EXEC = "bash_exec"           # Can execute bash commands
    DATABASE = "database"             # Can access database
    GIT_OPS = "git_ops"               # Can perform git operations

    # Special capabilities
    ALL = "all"  # Full access (use with caution)
    NONE = "none"  # Read-only mode


@dataclass
class AgentIdentity:
    """
    Unified identity of an agent in the system.

    Used for:
    - Agent registration and discovery
    - Capability-based access control
    - Message routing between agents
    """
    agent_id: str
    role: AgentRole
    name: Optional[str] = None
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set default name from role if not provided."""
        if self.name is None:
            self.name = self.role.value.title()

    def can_handle(self, capability: str) -> bool:
        """Check if agent can handle a capability."""
        if AgentCapability.ALL.value in self.capabilities:
            return True
        return capability in self.capabilities

    def has_capability(self, cap: AgentCapability) -> bool:
        """Check if agent has specific capability enum."""
        return self.can_handle(cap.value)


class TaskStatus(str, Enum):
    """Status of a task in execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlanningMode(str, Enum):
    """
    Planning modes inspired by Claude Code Plan Mode.
    """
    EXPLORATION = "exploration"  # Read-only exploration
    PLANNING = "planning"        # Generate plan
    EXECUTION = "execution"      # Execute plan


class ConfidenceLevel(str, Enum):
    """Confidence levels for plan steps."""
    CERTAIN = "certain"          # 0.9-1.0
    CONFIDENT = "confident"      # 0.7-0.9
    MODERATE = "moderate"        # 0.5-0.7
    LOW = "low"                  # 0.3-0.5
    SPECULATIVE = "speculative"  # 0.0-0.3

    @classmethod
    def from_score(cls, score: float) -> 'ConfidenceLevel':
        """Get level from numeric score."""
        if score >= 0.9:
            return cls.CERTAIN
        elif score >= 0.7:
            return cls.CONFIDENT
        elif score >= 0.5:
            return cls.MODERATE
        elif score >= 0.3:
            return cls.LOW
        return cls.SPECULATIVE


__all__ = [
    'AgentRole',
    'AgentPriority',
    'AgentCapability',
    'AgentIdentity',
    'TaskStatus',
    'PlanningMode',
    'ConfidenceLevel',
]
