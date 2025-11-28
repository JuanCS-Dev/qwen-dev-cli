"""
Health Check System.

SCALE & SUSTAIN Phase 3.2 - Connection Pooling.

Health monitoring for connections and services.

Author: JuanCS Dev
Date: 2025-11-26
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status for a service."""

    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: str = ""
    last_check: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @property
    def age_seconds(self) -> float:
        return time.time() - self.last_check


@dataclass
class HealthCheck:
    """
    Health check configuration and execution.

    Usage:
        check = HealthCheck(
            name="database",
            checker=check_db_connection,
            timeout=5.0,
            interval=30.0
        )

        result = await check.run()
        print(result.status)
    """

    name: str
    checker: Callable[[], Any]
    timeout: float = 5.0
    interval: float = 30.0
    failure_threshold: int = 3
    success_threshold: int = 1

    _consecutive_failures: int = field(default=0, init=False, repr=False)
    _consecutive_successes: int = field(default=0, init=False, repr=False)
    _last_result: Optional[ServiceHealth] = field(default=None, init=False, repr=False)

    async def run(self) -> ServiceHealth:
        """Execute the health check."""
        start_time = time.time()

        try:
            if asyncio.iscoroutinefunction(self.checker):
                await asyncio.wait_for(self.checker(), timeout=self.timeout)
            else:
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(
                    loop.run_in_executor(None, self.checker),
                    timeout=self.timeout
                )

            latency_ms = (time.time() - start_time) * 1000
            self._consecutive_successes += 1
            self._consecutive_failures = 0

            # Determine status based on thresholds
            if self._consecutive_successes >= self.success_threshold:
                status = HealthStatus.HEALTHY
            else:
                status = HealthStatus.DEGRADED

            self._last_result = ServiceHealth(
                name=self.name,
                status=status,
                latency_ms=latency_ms,
                message="Check passed"
            )

        except asyncio.TimeoutError:
            self._consecutive_failures += 1
            self._consecutive_successes = 0

            status = self._determine_failure_status()

            self._last_result = ServiceHealth(
                name=self.name,
                status=status,
                latency_ms=self.timeout * 1000,
                message=f"Check timed out after {self.timeout}s"
            )

        except Exception as e:
            self._consecutive_failures += 1
            self._consecutive_successes = 0

            latency_ms = (time.time() - start_time) * 1000
            status = self._determine_failure_status()

            self._last_result = ServiceHealth(
                name=self.name,
                status=status,
                latency_ms=latency_ms,
                message=f"Check failed: {str(e)}"
            )

        return self._last_result

    def _determine_failure_status(self) -> HealthStatus:
        """Determine status based on failure count."""
        if self._consecutive_failures >= self.failure_threshold:
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED

    @property
    def last_result(self) -> Optional[ServiceHealth]:
        """Get the last health check result."""
        return self._last_result


class HealthMonitor:
    """
    Monitors health of multiple services.

    Usage:
        monitor = HealthMonitor()
        monitor.register(HealthCheck("db", check_db))
        monitor.register(HealthCheck("redis", check_redis))

        await monitor.start()

        status = monitor.get_status()
        print(status.overall_status)

        await monitor.stop()
    """

    def __init__(self):
        self._checks: Dict[str, HealthCheck] = {}
        self._results: Dict[str, ServiceHealth] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []

    def register(self, check: HealthCheck) -> None:
        """Register a health check."""
        self._checks[check.name] = check

    def unregister(self, name: str) -> None:
        """Unregister a health check."""
        if name in self._checks:
            del self._checks[name]
        if name in self._results:
            del self._results[name]

    async def check_one(self, name: str) -> ServiceHealth:
        """Run a single health check."""
        if name not in self._checks:
            return ServiceHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="Health check not registered"
            )

        result = await self._checks[name].run()
        self._results[name] = result
        return result

    async def check_all(self) -> Dict[str, ServiceHealth]:
        """Run all health checks concurrently."""
        tasks = [
            self.check_one(name)
            for name in self._checks
        ]
        await asyncio.gather(*tasks)
        return self._results.copy()

    async def start(self) -> None:
        """Start continuous health monitoring."""
        if self._running:
            return

        self._running = True

        for name, check in self._checks.items():
            task = asyncio.create_task(self._monitor_loop(check))
            self._tasks.append(task)

    async def _monitor_loop(self, check: HealthCheck) -> None:
        """Continuous monitoring loop for a single check."""
        while self._running:
            result = await check.run()
            self._results[check.name] = result
            await asyncio.sleep(check.interval)

    async def stop(self) -> None:
        """Stop health monitoring."""
        self._running = False

        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()

    def get_status(self, name: Optional[str] = None) -> Dict[str, ServiceHealth]:
        """
        Get current health status.

        Args:
            name: Optional service name. If None, returns all.

        Returns:
            Dictionary of service names to health status
        """
        if name:
            if name in self._results:
                return {name: self._results[name]}
            return {name: ServiceHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="No health data available"
            )}
        return self._results.copy()

    @property
    def overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self._results:
            return HealthStatus.UNKNOWN

        statuses = [r.status for r in self._results.values()]

        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED
        return HealthStatus.UNKNOWN

    @property
    def is_healthy(self) -> bool:
        """Check if all services are healthy."""
        return self.overall_status == HealthStatus.HEALTHY


# Global health monitor
_global_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create the global health monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = HealthMonitor()
    return _global_monitor


__all__ = [
    'HealthCheck',
    'HealthStatus',
    'ServiceHealth',
    'HealthMonitor',
    'get_health_monitor',
]
