"""
Plugin Core System.

SCALE & SUSTAIN Phase 2.1 - Plugin Architecture.

Provides extensibility through a well-defined plugin interface.

Usage:
    from plugins.core import Plugin, PluginMetadata, PluginLoader, PluginRegistry

    class MyPlugin(Plugin):
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="my-plugin",
                version="1.0.0",
                description="My custom plugin",
                author="JuanCS"
            )

        async def activate(self, context: PluginContext) -> None:
            # Setup code here
            pass

        async def deactivate(self) -> None:
            # Cleanup code here
            pass

Author: JuanCS Dev
Date: 2025-11-26
"""

from .base import (
    Plugin,
    PluginMetadata,
    PluginPriority,
    PluginContext,
    PluginState,
)

from .loader import PluginLoader

from .registry import PluginRegistry

from .hooks import (
    PluginHook,
    HookType,
    HookResult,
)


__all__ = [
    # Base
    'Plugin',
    'PluginMetadata',
    'PluginPriority',
    'PluginContext',
    'PluginState',
    # Loader
    'PluginLoader',
    # Registry
    'PluginRegistry',
    # Hooks
    'PluginHook',
    'HookType',
    'HookResult',
]
