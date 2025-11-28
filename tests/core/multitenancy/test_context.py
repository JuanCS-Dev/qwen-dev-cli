"""
Tests for tenant context management.

SCALE & SUSTAIN Phase 3.4 validation.
"""

import asyncio
import pytest

from jdev_core.multitenancy import (
    Tenant,
    TenantContext,
    get_current_tenant,
    set_current_tenant,
    tenant_context,
)
from jdev_core.multitenancy.context import (
    require_tenant,
    require_active_tenant,
    TenantAware,
)


class TestTenantContext:
    """Test TenantContext class."""

    def test_context_creation(self):
        """Test basic context creation."""
        tenant = Tenant(name="Test")
        ctx = TenantContext(
            tenant=tenant,
            request_id="req-123",
            user_id="user-456"
        )

        assert ctx.tenant == tenant
        assert ctx.tenant_id == tenant.id
        assert ctx.request_id == "req-123"
        assert ctx.user_id == "user-456"

    def test_context_is_active(self):
        """Test is_active property."""
        tenant = Tenant(name="Test")
        ctx = TenantContext(tenant=tenant)

        assert ctx.is_active is False

        tenant.activate()
        assert ctx.is_active is True

    def test_context_attributes(self):
        """Test context attribute get/set."""
        tenant = Tenant(name="Test")
        ctx = TenantContext(tenant=tenant)

        ctx.set_attribute("custom", "value")
        assert ctx.get_attribute("custom") == "value"
        assert ctx.get_attribute("missing", "default") == "default"


class TestContextVariables:
    """Test contextvars-based context management."""

    def test_get_current_tenant_default_none(self):
        """Test get_current_tenant returns None by default."""
        assert get_current_tenant() is None

    def test_set_and_get_current_tenant(self):
        """Test setting and getting current tenant."""
        tenant = Tenant(name="Test")
        ctx = TenantContext(tenant=tenant)

        token = set_current_tenant(ctx)
        try:
            result = get_current_tenant()
            assert result == ctx
        finally:
            set_current_tenant(None)

    def test_tenant_context_manager(self):
        """Test tenant_context context manager."""
        tenant = Tenant(name="Test")

        with tenant_context(tenant) as ctx:
            assert get_current_tenant() == ctx
            assert ctx.tenant == tenant

        assert get_current_tenant() is None

    def test_nested_tenant_contexts(self):
        """Test nested tenant contexts."""
        tenant1 = Tenant(name="Outer")
        tenant2 = Tenant(name="Inner")

        with tenant_context(tenant1) as ctx1:
            assert get_current_tenant().tenant == tenant1

            with tenant_context(tenant2) as ctx2:
                assert get_current_tenant().tenant == tenant2

            # Back to outer context
            assert get_current_tenant().tenant == tenant1

        assert get_current_tenant() is None


class TestRequireTenant:
    """Test require_tenant functions."""

    def test_require_tenant_raises_without_context(self):
        """Test require_tenant raises when no context."""
        with pytest.raises(RuntimeError) as exc_info:
            require_tenant()

        assert "No tenant context" in str(exc_info.value)

    def test_require_tenant_returns_context(self):
        """Test require_tenant returns context when set."""
        tenant = Tenant(name="Test")

        with tenant_context(tenant) as ctx:
            result = require_tenant()
            assert result == ctx

    def test_require_active_tenant_raises_for_inactive(self):
        """Test require_active_tenant raises for inactive tenant."""
        tenant = Tenant(name="Test")  # Status is PENDING

        with tenant_context(tenant):
            with pytest.raises(RuntimeError) as exc_info:
                require_active_tenant()

            assert "not active" in str(exc_info.value)

    def test_require_active_tenant_succeeds_for_active(self):
        """Test require_active_tenant succeeds for active tenant."""
        tenant = Tenant(name="Test")
        tenant.activate()

        with tenant_context(tenant) as ctx:
            result = require_active_tenant()
            assert result == ctx


class TestTenantAware:
    """Test TenantAware mixin."""

    class MyService(TenantAware):
        """Test service using TenantAware mixin."""

        def get_tenant_name(self):
            if self.tenant:
                return self.tenant.name
            return None

    def test_tenant_aware_no_context(self):
        """Test TenantAware when no context."""
        service = self.MyService()

        assert service.tenant_context is None
        assert service.tenant is None
        assert service.tenant_id is None
        assert service.get_tenant_name() is None

    def test_tenant_aware_with_context(self):
        """Test TenantAware with active context."""
        tenant = Tenant(name="TestCorp")
        service = self.MyService()

        with tenant_context(tenant):
            assert service.tenant_context is not None
            assert service.tenant == tenant
            assert service.tenant_id == tenant.id
            assert service.get_tenant_name() == "TestCorp"

    def test_tenant_aware_require_tenant(self):
        """Test TenantAware.require_tenant method."""
        service = self.MyService()

        with pytest.raises(RuntimeError):
            service.require_tenant()

        tenant = Tenant(name="Test")
        with tenant_context(tenant) as ctx:
            result = service.require_tenant()
            assert result == ctx


class TestAsyncContextIsolation:
    """Test context isolation in async code."""

    @pytest.mark.asyncio
    async def test_context_isolation_between_tasks(self):
        """Test context is isolated between async tasks."""
        tenant1 = Tenant(name="Task1")
        tenant2 = Tenant(name="Task2")
        results = {}

        async def task(name, tenant):
            with tenant_context(tenant):
                await asyncio.sleep(0.01)
                results[name] = get_current_tenant().tenant.name

        await asyncio.gather(
            task("t1", tenant1),
            task("t2", tenant2),
        )

        assert results["t1"] == "Task1"
        assert results["t2"] == "Task2"

    @pytest.mark.asyncio
    async def test_context_preserved_across_await(self):
        """Test context is preserved across await points."""
        tenant = Tenant(name="Persistent")

        with tenant_context(tenant):
            before = get_current_tenant().tenant.name
            await asyncio.sleep(0.01)
            after = get_current_tenant().tenant.name

            assert before == "Persistent"
            assert after == "Persistent"
