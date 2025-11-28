"""
Governance Interface.

SCALE & SUSTAIN Phase 2.2 - Interface Extraction.

Defines interfaces for governance/security:
- IGovernance: Security policy enforcement
- RiskAssessment: Risk evaluation result

Author: JuanCS Dev
Date: 2025-11-26
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for actions."""
    SAFE = 0           # No risk, auto-approve
    LOW = 1            # Minor risk, soft confirmation
    MEDIUM = 2         # Moderate risk, explicit confirmation
    HIGH = 3           # High risk, strong confirmation
    CRITICAL = 4       # Critical risk, requires typed confirmation
    BLOCKED = 5        # Action is blocked


@dataclass
class RiskAssessment:
    """
    Risk assessment for an action.

    Attributes:
        level: Risk level
        score: Numeric risk score (0.0 to 1.0)
        reasons: List of risk reasons
        mitigations: Suggested mitigations
        allow: Whether action should be allowed
        confirmation_required: Type of confirmation needed
    """
    level: RiskLevel
    score: float
    reasons: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    allow: bool = True
    confirmation_required: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def safe(cls) -> 'RiskAssessment':
        """Create safe assessment."""
        return cls(level=RiskLevel.SAFE, score=0.0, allow=True)

    @classmethod
    def blocked(cls, reasons: List[str]) -> 'RiskAssessment':
        """Create blocked assessment."""
        return cls(
            level=RiskLevel.BLOCKED,
            score=1.0,
            reasons=reasons,
            allow=False
        )


@dataclass
class GovernancePolicy:
    """Governance policy definition."""
    name: str
    description: str
    rules: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True


class IGovernance(ABC):
    """
    Interface for governance/security.

    Enforces security policies on actions.

    Example:
        gov = MyGovernance()
        assessment = gov.assess_risk("rm -rf /")
        if not assessment.allow:
            print("Action blocked:", assessment.reasons)
    """

    @abstractmethod
    def assess_risk(self, action: str) -> RiskAssessment:
        """
        Assess risk of an action.

        Args:
            action: Action to assess

        Returns:
            Risk assessment result
        """
        pass

    @abstractmethod
    def is_allowed(self, action: str) -> bool:
        """
        Check if action is allowed.

        Args:
            action: Action to check

        Returns:
            True if allowed
        """
        pass

    @abstractmethod
    def get_confirmation_prompt(
        self,
        action: str,
        assessment: RiskAssessment
    ) -> str:
        """
        Get confirmation prompt for action.

        Args:
            action: Action requiring confirmation
            assessment: Risk assessment

        Returns:
            Prompt string for user
        """
        pass

    def add_policy(self, policy: GovernancePolicy) -> None:
        """Add a governance policy."""
        pass

    def remove_policy(self, name: str) -> bool:
        """Remove a governance policy."""
        return False

    def get_policies(self) -> List[GovernancePolicy]:
        """Get all active policies."""
        return []


class IConstitutionalAI(ABC):
    """
    Interface for Constitutional AI governance.

    Provides Justiça-style governance for the system.
    """

    @abstractmethod
    async def evaluate(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate action against constitutional principles.

        Args:
            action: Action to evaluate
            context: Evaluation context

        Returns:
            Evaluation result with verdict
        """
        pass

    @abstractmethod
    async def generate_report(self) -> str:
        """Generate governance report."""
        pass


__all__ = [
    'IGovernance',
    'IConstitutionalAI',
    'RiskAssessment',
    'RiskLevel',
    'GovernancePolicy',
]
