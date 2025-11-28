"""
Tenant Context Management.

SCALE & SUSTAIN Phase 3.4 - Multi-Tenant.

Thread/async-safe tenant context using contextvars.

Author: JuanCS Dev
Date: 2025-11-26
"""

import contextvars
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .tenant import Tenant


# Context variable for current tenant
_current_tenant: contextvars.ContextVar[Optional['TenantContext']] = \
    contextvars.ContextVar('current_tenant', default=None)


@dataclass
class TenantContext:
    """
    Context for current tenant operation.

    Carries tenant information through the request/operation lifecycle.
    """

    tenant: Tenant
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def tenant_id(self) -> str:
        """Get tenant ID."""
        return self.tenant.id

    @property
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.tenant.is_active

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get a context attribute."""
        return self.attributes.get(key, default)

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a context attribute."""
        self.attributes[key] = value


def get_current_tenant() -> Optional[TenantContext]:
    """
    Get the current tenant context.

    Returns:
        TenantContext if set, None otherwise
    """
    return _current_tenant.get()


def set_current_tenant(context: Optional[TenantContext]) -> contextvars.Token:
    """
    Set the current tenant context.

    Args:
        context: TenantContext to set

    Returns:
        Token for resetting to previous value
    """
    return _current_tenant.set(context)


def reset_tenant(token: contextvars.Token) -> None:
    """
    Reset tenant context to previous value.

    Args:
        token: Token from set_current_tenant
    """
    _current_tenant.reset(token)


@contextmanager
def tenant_context(tenant: Tenant, **kwargs):
    """
    Context manager for tenant scope.

    Usage:
        with tenant_context(my_tenant) as ctx:
            # Operations run in tenant context
            do_something()

    Args:
        tenant: Tenant for this context
        **kwargs: Additional context attributes
    """
    context = TenantContext(
        tenant=tenant,
        **kwargs
    )
    token = set_current_tenant(context)
    try:
        yield context
    finally:
        reset_tenant(token)


def require_tenant() -> TenantContext:
    """
    Get current tenant context, raising if not set.

    Returns:
        Current TenantContext

    Raises:
        RuntimeError: If no tenant context is set
    """
    context = get_current_tenant()
    if context is None:
        raise RuntimeError("No tenant context set. Use tenant_context() or set_current_tenant().")
    return context


def require_active_tenant() -> TenantContext:
    """
    Get current tenant context, requiring it to be active.

    Returns:
        Current TenantContext

    Raises:
        RuntimeError: If no tenant context or tenant is not active
    """
    context = require_tenant()
    if not context.is_active:
        raise RuntimeError(f"Tenant {context.tenant_id} is not active")
    return context


class TenantAware:
    """
    Mixin for tenant-aware classes.

    Classes that inherit from this will automatically use the current tenant context.
    """

    @property
    def tenant_context(self) -> Optional[TenantContext]:
        """Get current tenant context."""
        return get_current_tenant()

    @property
    def tenant(self) -> Optional[Tenant]:
        """Get current tenant."""
        ctx = self.tenant_context
        return ctx.tenant if ctx else None

    @property
    def tenant_id(self) -> Optional[str]:
        """Get current tenant ID."""
        tenant = self.tenant
        return tenant.id if tenant else None

    def require_tenant(self) -> TenantContext:
        """Require tenant context to be set."""
        return require_tenant()


__all__ = [
    'TenantContext',
    'get_current_tenant',
    'set_current_tenant',
    'reset_tenant',
    'tenant_context',
    'require_tenant',
    'require_active_tenant',
    'TenantAware',
]
