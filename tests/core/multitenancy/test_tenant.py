"""
Tests for tenant management.

SCALE & SUSTAIN Phase 3.4 validation.
"""

import pytest

from jdev_core.multitenancy import (
    Tenant,
    TenantConfig,
    TenantStatus,
    TenantTier,
)
from jdev_core.multitenancy.tenant import TenantRegistry


class TestTenantTier:
    """Test TenantTier enum."""

    def test_tier_values(self):
        """Test all tier values exist."""
        assert TenantTier.FREE.value == "free"
        assert TenantTier.BASIC.value == "basic"
        assert TenantTier.PRO.value == "pro"
        assert TenantTier.ENTERPRISE.value == "enterprise"


class TestTenantStatus:
    """Test TenantStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert TenantStatus.ACTIVE.value == "active"
        assert TenantStatus.SUSPENDED.value == "suspended"
        assert TenantStatus.PENDING.value == "pending"
        assert TenantStatus.DELETED.value == "deleted"


class TestTenantConfig:
    """Test TenantConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = TenantConfig()

        assert config.requests_per_minute == 60
        assert config.max_tokens_per_request == 4096
        assert config.monthly_token_quota == 100000

    def test_config_for_free_tier(self):
        """Test FREE tier configuration."""
        config = TenantConfig.for_tier(TenantTier.FREE)

        assert config.requests_per_minute == 10
        assert config.max_concurrent_requests == 1
        assert config.custom_agents_enabled is False

    def test_config_for_pro_tier(self):
        """Test PRO tier configuration."""
        config = TenantConfig.for_tier(TenantTier.PRO)

        assert config.requests_per_minute == 100
        assert config.max_concurrent_requests == 10
        assert config.custom_agents_enabled is True
        assert config.plugin_enabled is True

    def test_config_for_enterprise_tier(self):
        """Test ENTERPRISE tier configuration."""
        config = TenantConfig.for_tier(TenantTier.ENTERPRISE)

        assert config.requests_per_minute == 500
        assert config.max_tokens_per_request == 32768
        assert config.monthly_token_quota == 10000000


class TestTenant:
    """Test Tenant entity."""

    def test_tenant_creation(self):
        """Test basic tenant creation."""
        tenant = Tenant(name="Test Corp")

        assert tenant.name == "Test Corp"
        assert tenant.slug == "test-corp"
        assert tenant.status == TenantStatus.PENDING
        assert tenant.tier == TenantTier.FREE
        assert tenant.id is not None

    def test_tenant_is_active(self):
        """Test is_active property."""
        tenant = Tenant(name="Test")

        assert tenant.is_active is False

        tenant.activate()
        assert tenant.is_active is True

    def test_tenant_activate(self):
        """Test tenant activation."""
        tenant = Tenant(name="Test")
        tenant.activate()

        assert tenant.status == TenantStatus.ACTIVE

    def test_tenant_suspend(self):
        """Test tenant suspension."""
        tenant = Tenant(name="Test")
        tenant.activate()
        tenant.suspend()

        assert tenant.status == TenantStatus.SUSPENDED

    def test_tenant_delete(self):
        """Test tenant deletion."""
        tenant = Tenant(name="Test")
        tenant.delete()

        assert tenant.status == TenantStatus.DELETED

    def test_tenant_upgrade_tier(self):
        """Test tier upgrade."""
        tenant = Tenant(name="Test", tier=TenantTier.FREE)

        tenant.upgrade_tier(TenantTier.PRO)

        assert tenant.tier == TenantTier.PRO
        assert tenant.config.custom_agents_enabled is True

    def test_tenant_to_dict(self):
        """Test tenant serialization."""
        tenant = Tenant(name="Test Corp")
        d = tenant.to_dict()

        assert d["name"] == "Test Corp"
        assert d["slug"] == "test-corp"
        assert d["status"] == "pending"
        assert d["tier"] == "free"

    def test_tenant_from_dict(self):
        """Test tenant deserialization."""
        data = {
            "id": "test-id",
            "name": "Restored Corp",
            "status": "active",
            "tier": "pro",
        }
        tenant = Tenant.from_dict(data)

        assert tenant.id == "test-id"
        assert tenant.name == "Restored Corp"
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.tier == TenantTier.PRO


class TestTenantRegistry:
    """Test TenantRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a test registry."""
        return TenantRegistry()

    def test_register_tenant(self, registry):
        """Test registering a tenant."""
        tenant = Tenant(name="Test")
        registry.register(tenant)

        assert registry.get(tenant.id) == tenant

    def test_get_by_slug(self, registry):
        """Test getting tenant by slug."""
        tenant = Tenant(name="My Company")
        registry.register(tenant)

        result = registry.get_by_slug("my-company")
        assert result == tenant

    def test_list_tenants(self, registry):
        """Test listing all tenants."""
        t1 = Tenant(name="One")
        t2 = Tenant(name="Two")
        t1.activate()

        registry.register(t1)
        registry.register(t2)

        all_tenants = registry.list()
        assert len(all_tenants) == 2

        active_tenants = registry.list(status=TenantStatus.ACTIVE)
        assert len(active_tenants) == 1

    def test_remove_tenant(self, registry):
        """Test removing a tenant."""
        tenant = Tenant(name="ToRemove")
        registry.register(tenant)

        result = registry.remove(tenant.id)
        assert result is True
        assert registry.get(tenant.id) is None
