"""
Connection Management.

SCALE & SUSTAIN Phase 3.2 - Connection Pooling.

Provides connection pooling and management for:
- Database connections (SQLite, PostgreSQL)
- HTTP clients
- External services (Redis, etc.)

Author: JuanCS Dev
Date: 2025-11-26
"""

from .pool import (
    ConnectionPool,
    PoolConfig,
    PoolStats,
    PoolExhaustedError,
)

from .manager import (
    ConnectionManager,
    ConnectionConfig,
    ConnectionType,
)

from .health import (
    HealthCheck,
    HealthStatus,
    ServiceHealth,
)

__all__ = [
    # Pool
    'ConnectionPool',
    'PoolConfig',
    'PoolStats',
    'PoolExhaustedError',
    # Manager
    'ConnectionManager',
    'ConnectionConfig',
    'ConnectionType',
    # Health
    'HealthCheck',
    'HealthStatus',
    'ServiceHealth',
]
