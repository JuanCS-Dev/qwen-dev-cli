"""
Circuit Breaker Pattern - Resilience Engineering
================================================

Extracted from llm_client.py as part of SCALE & SUSTAIN refactoring.

Prevents cascading failures by stopping requests to failing services.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service failing, requests rejected immediately
- HALF_OPEN: Testing recovery, limited requests allowed

Author: JuanCS Dev
Date: 2025-11-27
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND CONFIGURATION
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int = 5       # Failures before opening
    success_threshold: int = 2       # Successes before closing from half-open
    timeout: float = 30.0            # Seconds before trying half-open
    half_open_max_calls: int = 3     # Max calls in half-open state

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")
        if self.half_open_max_calls < 1:
            raise ValueError("half_open_max_calls must be >= 1")


@dataclass
class CircuitBreakerStats:
    """Statistics for observability."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: List[Tuple[str, float]] = field(default_factory=list)
    last_failure_time: Optional[float] = None
    last_failure_reason: Optional[str] = None


# =============================================================================
# EXCEPTIONS
# =============================================================================

class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and rejecting requests."""

    def __init__(self, breaker_name: str, retry_after: float):
        self.breaker_name = breaker_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker '{breaker_name}' is open. Retry after {retry_after:.1f}s"
        )


# =============================================================================
# CIRCUIT BREAKER IMPLEMENTATION
# =============================================================================

class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation.

    Prevents cascading failures by stopping requests to failing services.

    Usage:
        breaker = CircuitBreaker("api", config)

        # Check before call
        if await breaker.can_execute():
            try:
                result = await external_service()
                breaker.record_success()
            except Exception as e:
                breaker.record_failure(str(e))
        else:
            raise CircuitBreakerOpen(breaker.name, breaker.retry_after)

    Attributes:
        name: Identifier for this circuit breaker
        config: Configuration settings
        stats: Observability statistics
    """

    def __init__(
        self,
        name: str = "default",
        config: Optional[CircuitBreakerConfig] = None
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for logging and observability
            config: Configuration settings (uses defaults if None)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
        self.stats = CircuitBreakerStats()

    @property
    def state(self) -> CircuitState:
        """
        Get current state, checking for timeout transition.

        Automatically transitions from OPEN to HALF_OPEN after timeout.
        """
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.config.timeout:
                    return CircuitState.HALF_OPEN
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting requests)."""
        return self.state == CircuitState.OPEN

    @property
    def retry_after(self) -> float:
        """Seconds until circuit may transition to half-open."""
        if self._state != CircuitState.OPEN or not self._last_failure_time:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        remaining = self.config.timeout - elapsed
        return max(0.0, remaining)

    def _transition_to(self, new_state: CircuitState) -> None:
        """
        Transition to a new state with logging.

        Args:
            new_state: Target state to transition to
        """
        old_state = self._state
        self._state = new_state
        self.stats.state_changes.append((new_state.value, time.time()))

        logger.info(
            f"CircuitBreaker '{self.name}': {old_state.value} -> {new_state.value}"
        )

        if new_state == CircuitState.OPEN:
            self._last_failure_time = time.time()
            self._half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0

    def record_success(self) -> None:
        """Record a successful call."""
        self.stats.total_calls += 1
        self.stats.successful_calls += 1

        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def record_failure(self, reason: str = "") -> None:
        """
        Record a failed call.

        Args:
            reason: Description of failure for logging
        """
        self.stats.total_calls += 1
        self.stats.failed_calls += 1
        self.stats.last_failure_time = time.time()
        self.stats.last_failure_reason = reason

        if reason:
            logger.warning(f"CircuitBreaker '{self.name}' failure: {reason[:100]}")

        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open goes back to open
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    async def can_execute(self) -> bool:
        """
        Check if a call can be executed.

        Returns:
            True if call is allowed, False if circuit is open
        """
        async with self._lock:
            current_state = self.state

            if current_state == CircuitState.CLOSED:
                return True

            if current_state == CircuitState.OPEN:
                self.stats.rejected_calls += 1
                return False

            if current_state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                self.stats.rejected_calls += 1
                return False

            return False

    def reset(self) -> None:
        """Reset circuit breaker to initial state (CLOSED)."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_calls = 0
        logger.info(f"CircuitBreaker '{self.name}' reset to CLOSED")

    def get_status(self) -> Dict[str, Any]:
        """
        Get circuit breaker status for observability.

        Returns:
            Dictionary with current state and statistics
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "retry_after": self.retry_after,
            "stats": {
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "last_failure_time": self.stats.last_failure_time,
                "last_failure_reason": self.stats.last_failure_reason,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
                "half_open_max_calls": self.config.half_open_max_calls,
            }
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerStats",
    "CircuitBreaker",
    "CircuitBreakerOpen",
]
