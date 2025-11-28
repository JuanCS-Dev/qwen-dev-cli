"""
Multi-Tenant System.

SCALE & SUSTAIN Phase 3.4 - Multi-Tenant.

Provides tenant isolation and management:
- Tenant context management
- Resource isolation
- Rate limiting per tenant
- Quota management

Author: JuanCS Dev
Date: 2025-11-26
"""

from .tenant import (
    Tenant,
    TenantConfig,
    TenantStatus,
    TenantTier,
)

from .context import (
    TenantContext,
    get_current_tenant,
    set_current_tenant,
    tenant_context,
)

from .isolation import (
    TenantIsolation,
    IsolationLevel,
    ResourceScope,
)

from .quotas import (
    QuotaManager,
    Quota,
    QuotaUsage,
    QuotaExceededError,
)

__all__ = [
    # Tenant
    'Tenant',
    'TenantConfig',
    'TenantStatus',
    'TenantTier',
    # Context
    'TenantContext',
    'get_current_tenant',
    'set_current_tenant',
    'tenant_context',
    # Isolation
    'TenantIsolation',
    'IsolationLevel',
    'ResourceScope',
    # Quotas
    'QuotaManager',
    'Quota',
    'QuotaUsage',
    'QuotaExceededError',
]
