"""
Interfaces Module - Abstract Base Classes for Bridge Managers.

Part of SCALE & SUSTAIN Phase 1.1 - Bridge Refactoring.
These interfaces enable:
- Testability via dependency injection
- Loose coupling between components
- Plugin system preparation (Phase 2)

Author: JuanCS Dev
Date: 2025-11-26
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


class ITodoManager(ABC):
    """Interface for TODO management."""

    @abstractmethod
    def get_todos(self) -> List[Dict[str, Any]]:
        """Get all TODO items."""
        pass

    @abstractmethod
    def add_todo(self, text: str) -> None:
        """Add a new TODO item."""
        pass

    @abstractmethod
    def update_todo(self, index: int, done: bool) -> bool:
        """Update TODO status. Returns True if successful."""
        pass

    @abstractmethod
    def clear_todos(self) -> None:
        """Clear all TODO items."""
        pass


class IStatusManager(ABC):
    """Interface for system status and health checks."""

    @abstractmethod
    def check_health(self) -> Dict[str, Dict[str, Any]]:
        """Check system health for all components."""
        pass

    @abstractmethod
    def get_permissions(self) -> Dict[str, bool]:
        """Get current system permissions."""
        pass

    @abstractmethod
    def set_sandbox(self, enabled: bool) -> None:
        """Enable or disable sandbox mode."""
        pass

    @abstractmethod
    def is_sandbox_enabled(self) -> bool:
        """Check if sandbox mode is enabled."""
        pass


class IPullRequestManager(ABC):
    """Interface for GitHub PR operations."""

    @abstractmethod
    async def create_pull_request(
        self,
        title: str,
        body: Optional[str] = None,
        base: str = "main",
        draft: bool = False
    ) -> Dict[str, Any]:
        """Create a GitHub pull request."""
        pass

    @abstractmethod
    def get_pr_template(self) -> str:
        """Get PR template if exists."""
        pass


class IMemoryManager(ABC):
    """Interface for persistent memory (MEMORY.md)."""

    @abstractmethod
    def read_memory(self, scope: str = "project") -> Dict[str, Any]:
        """Read memory from MEMORY.md file."""
        pass

    @abstractmethod
    def write_memory(
        self,
        content: str,
        scope: str = "project",
        append: bool = False
    ) -> Dict[str, Any]:
        """Write to MEMORY.md file."""
        pass

    @abstractmethod
    def remember(self, note: str, scope: str = "project") -> Dict[str, Any]:
        """Add a note to memory."""
        pass


class IContextManager(ABC):
    """Interface for conversation context management."""

    @abstractmethod
    def compact_context(self, focus: Optional[str] = None) -> Dict[str, Any]:
        """Compact conversation context."""
        pass

    @abstractmethod
    def get_token_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        pass

    @abstractmethod
    def get_context(self) -> List[Dict[str, Any]]:
        """Get current conversation context."""
        pass

    @abstractmethod
    def add_context(self, role: str, content: str) -> None:
        """Add message to context."""
        pass

    @abstractmethod
    def clear_context(self) -> None:
        """Clear conversation context."""
        pass


class IAuthenticationManager(ABC):
    """Interface for API key authentication."""

    @abstractmethod
    def login(
        self,
        provider: str = "gemini",
        api_key: Optional[str] = None,
        scope: str = "global"
    ) -> Dict[str, Any]:
        """Login/configure API key for a provider."""
        pass

    @abstractmethod
    def logout(
        self,
        provider: Optional[str] = None,
        scope: str = "all"
    ) -> Dict[str, Any]:
        """Logout/remove API key for a provider."""
        pass

    @abstractmethod
    def get_auth_status(self) -> Dict[str, Any]:
        """Get authentication status for all providers."""
        pass


# Re-export all interfaces
__all__ = [
    'ITodoManager',
    'IStatusManager',
    'IPullRequestManager',
    'IMemoryManager',
    'IContextManager',
    'IAuthenticationManager',
]
