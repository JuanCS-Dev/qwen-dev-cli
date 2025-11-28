"""
Tenant Definition.

SCALE & SUSTAIN Phase 3.4 - Multi-Tenant.

Core tenant model and configuration.

Author: JuanCS Dev
Date: 2025-11-26
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TenantStatus(Enum):
    """Tenant lifecycle status."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class TenantTier(Enum):
    """Tenant subscription tier."""

    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TenantConfig:
    """Tenant configuration and limits."""

    # Rate limits
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000

    # Resource limits
    max_tokens_per_request: int = 4096
    max_concurrent_requests: int = 5
    max_sessions: int = 10
    max_storage_mb: int = 100

    # Features
    allowed_models: List[str] = field(default_factory=lambda: ["default"])
    allowed_tools: List[str] = field(default_factory=list)
    custom_agents_enabled: bool = False
    plugin_enabled: bool = False

    # Quotas
    monthly_token_quota: int = 100000
    monthly_request_quota: int = 10000

    @classmethod
    def for_tier(cls, tier: TenantTier) -> 'TenantConfig':
        """Get default config for a tier."""
        configs = {
            TenantTier.FREE: cls(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=500,
                max_tokens_per_request=2048,
                max_concurrent_requests=1,
                max_sessions=3,
                max_storage_mb=10,
                monthly_token_quota=10000,
                monthly_request_quota=500,
            ),
            TenantTier.BASIC: cls(
                requests_per_minute=30,
                requests_per_hour=500,
                requests_per_day=5000,
                max_tokens_per_request=4096,
                max_concurrent_requests=3,
                max_sessions=10,
                max_storage_mb=100,
                monthly_token_quota=100000,
                monthly_request_quota=5000,
            ),
            TenantTier.PRO: cls(
                requests_per_minute=100,
                requests_per_hour=2000,
                requests_per_day=20000,
                max_tokens_per_request=8192,
                max_concurrent_requests=10,
                max_sessions=50,
                max_storage_mb=1000,
                custom_agents_enabled=True,
                plugin_enabled=True,
                monthly_token_quota=1000000,
                monthly_request_quota=20000,
            ),
            TenantTier.ENTERPRISE: cls(
                requests_per_minute=500,
                requests_per_hour=10000,
                requests_per_day=100000,
                max_tokens_per_request=32768,
                max_concurrent_requests=50,
                max_sessions=500,
                max_storage_mb=10000,
                custom_agents_enabled=True,
                plugin_enabled=True,
                monthly_token_quota=10000000,
                monthly_request_quota=100000,
            ),
        }
        return configs.get(tier, cls())


@dataclass
class Tenant:
    """Tenant entity."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    slug: str = ""
    status: TenantStatus = TenantStatus.PENDING
    tier: TenantTier = TenantTier.FREE
    config: TenantConfig = field(default_factory=TenantConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')

    @property
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.status == TenantStatus.ACTIVE

    def activate(self) -> None:
        """Activate the tenant."""
        self.status = TenantStatus.ACTIVE
        self.updated_at = time.time()

    def suspend(self) -> None:
        """Suspend the tenant."""
        self.status = TenantStatus.SUSPENDED
        self.updated_at = time.time()

    def delete(self) -> None:
        """Mark tenant as deleted."""
        self.status = TenantStatus.DELETED
        self.updated_at = time.time()

    def upgrade_tier(self, new_tier: TenantTier) -> None:
        """Upgrade to a new tier."""
        self.tier = new_tier
        self.config = TenantConfig.for_tier(new_tier)
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status.value,
            'tier': self.tier.value,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tenant':
        """Create from dictionary."""
        tenant = cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
        )
        if 'status' in data:
            tenant.status = TenantStatus(data['status'])
        if 'tier' in data:
            tenant.tier = TenantTier(data['tier'])
            tenant.config = TenantConfig.for_tier(tenant.tier)
        return tenant


class TenantRegistry:
    """
    In-memory tenant registry.

    For production, replace with database-backed implementation.
    """

    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
        self._by_slug: Dict[str, str] = {}

    def register(self, tenant: Tenant) -> None:
        """Register a tenant."""
        self._tenants[tenant.id] = tenant
        self._by_slug[tenant.slug] = tenant.id

    def get(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)

    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        tenant_id = self._by_slug.get(slug)
        if tenant_id:
            return self._tenants.get(tenant_id)
        return None

    def list(self, status: Optional[TenantStatus] = None) -> List[Tenant]:
        """List tenants, optionally filtered by status."""
        tenants = list(self._tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        return tenants

    def remove(self, tenant_id: str) -> bool:
        """Remove a tenant."""
        if tenant_id in self._tenants:
            tenant = self._tenants.pop(tenant_id)
            if tenant.slug in self._by_slug:
                del self._by_slug[tenant.slug]
            return True
        return False


# Global registry
_global_registry: Optional[TenantRegistry] = None


def get_tenant_registry() -> TenantRegistry:
    """Get global tenant registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = TenantRegistry()
    return _global_registry


__all__ = [
    'Tenant',
    'TenantConfig',
    'TenantStatus',
    'TenantTier',
    'TenantRegistry',
    'get_tenant_registry',
]
