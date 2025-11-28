"""
Bridge Managers Module.

SCALE & SUSTAIN Phase 1.1 - Manager Extraction.

Extracted from shell_main.py to reduce complexity and improve testability.

Components:
- ConfigManager: Configuration management
- CacheManager: Caching operations
- SessionManager: Session state management
- ToolManager: Tool registration and execution
- ProviderManager: LLM provider management
- AuthenticationManager: Authentication and authorization

Author: JuanCS Dev
Date: 2025-11-26
"""

from .config_manager import ConfigManager, ConfigScope
from .cache_manager import CacheManager, CacheEntry, CacheStats
from .session_manager import SessionManager, SessionState, SessionConfig
from .tool_manager import ToolManager, ToolRegistration, ToolExecutionContext
from .provider_manager import ProviderManager, ProviderConfig, ProviderStatus
from .auth_manager import AuthenticationManager, AuthToken, AuthScope

__all__ = [
    # Config
    'ConfigManager',
    'ConfigScope',
    # Cache
    'CacheManager',
    'CacheEntry',
    'CacheStats',
    # Session
    'SessionManager',
    'SessionState',
    'SessionConfig',
    # Tool
    'ToolManager',
    'ToolRegistration',
    'ToolExecutionContext',
    # Provider
    'ProviderManager',
    'ProviderConfig',
    'ProviderStatus',
    # Auth
    'AuthenticationManager',
    'AuthToken',
    'AuthScope',
]
