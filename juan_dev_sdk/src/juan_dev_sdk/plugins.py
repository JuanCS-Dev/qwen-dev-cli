"""
Plugin Builder.

SCALE & SUSTAIN Phase 2.3 - SDK Plugin Creation.

Helpers for creating custom plugins.

Author: JuanCS Dev
Date: 2025-11-26
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional


@dataclass
class PluginConfig:
    """Plugin configuration."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginBuilder:
    """
    Builder for creating custom plugins.

    Usage:
        plugin = (PluginBuilder("my-plugin", "1.0.0")
            .description("My awesome plugin")
            .author("JuanCS")
            .provides(["my-feature"])
            .on_activate(my_activate_fn)
            .on_command("mycommand", my_command_handler)
            .build())
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize builder with plugin name and version."""
        self._config = PluginConfig(
            name=name,
            version=version,
            description="",
            author=""
        )
        self._activate_fn: Optional[Callable] = None
        self._deactivate_fn: Optional[Callable] = None
        self._command_handlers: Dict[str, Callable] = {}
        self._tool_handlers: Dict[str, Callable] = {}

    def description(self, desc: str) -> 'PluginBuilder':
        """Set plugin description."""
        self._config.description = desc
        return self

    def author(self, author: str) -> 'PluginBuilder':
        """Set plugin author."""
        self._config.author = author
        return self

    def dependency(self, dep: str) -> 'PluginBuilder':
        """Add a dependency."""
        self._config.dependencies.append(dep)
        return self

    def dependencies(self, deps: List[str]) -> 'PluginBuilder':
        """Set dependencies list."""
        self._config.dependencies = deps
        return self

    def provides(self, caps: List[str]) -> 'PluginBuilder':
        """Set provided capabilities."""
        self._config.provides = caps
        return self

    def metadata(self, **kwargs) -> 'PluginBuilder':
        """Add metadata."""
        self._config.metadata.update(kwargs)
        return self

    def on_activate(self, fn: Callable) -> 'PluginBuilder':
        """Set activation handler."""
        self._activate_fn = fn
        return self

    def on_deactivate(self, fn: Callable) -> 'PluginBuilder':
        """Set deactivation handler."""
        self._deactivate_fn = fn
        return self

    def on_command(self, command: str, handler: Callable) -> 'PluginBuilder':
        """Register command handler."""
        self._command_handlers[command] = handler
        return self

    def on_tool(self, tool_name: str, handler: Callable) -> 'PluginBuilder':
        """Register tool intercept handler."""
        self._tool_handlers[tool_name] = handler
        return self

    def build(self) -> 'CustomPlugin':
        """Build the plugin."""
        if not self._config.description:
            raise ValueError("Plugin description is required")
        if not self._config.author:
            raise ValueError("Plugin author is required")

        return CustomPlugin(
            self._config,
            self._activate_fn,
            self._deactivate_fn,
            self._command_handlers,
            self._tool_handlers
        )


class CustomPlugin:
    """Custom plugin created via builder."""

    def __init__(
        self,
        config: PluginConfig,
        activate_fn: Optional[Callable] = None,
        deactivate_fn: Optional[Callable] = None,
        command_handlers: Dict[str, Callable] = None,
        tool_handlers: Dict[str, Callable] = None
    ):
        self.config = config
        self._activate_fn = activate_fn
        self._deactivate_fn = deactivate_fn
        self._command_handlers = command_handlers or {}
        self._tool_handlers = tool_handlers or {}
        self._context = None

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def version(self) -> str:
        return self.config.version

    @property
    def description(self) -> str:
        return self.config.description

    async def activate(self, context: Any) -> None:
        """Activate the plugin."""
        self._context = context
        if self._activate_fn:
            result = self._activate_fn(context)
            if hasattr(result, '__await__'):
                await result

    async def deactivate(self) -> None:
        """Deactivate the plugin."""
        if self._deactivate_fn:
            result = self._deactivate_fn()
            if hasattr(result, '__await__'):
                await result
        self._context = None

    def on_command(self, command: str, args: str) -> Optional[Any]:
        """Handle command."""
        handler = self._command_handlers.get(command)
        if handler:
            return handler(args)
        return None

    def on_tool_execute(self, tool_name: str, params: Dict) -> Optional[Any]:
        """Intercept tool execution."""
        handler = self._tool_handlers.get(tool_name)
        if handler:
            return handler(params)
        return None


def create_plugin(
    name: str,
    version: str,
    description: str,
    author: str,
    activate_fn: Optional[Callable] = None,
) -> CustomPlugin:
    """
    Create a custom plugin.

    Shorthand for PluginBuilder.

    Args:
        name: Plugin name
        version: Plugin version
        description: Plugin description
        author: Plugin author
        activate_fn: Optional activation handler

    Returns:
        Custom plugin instance
    """
    builder = (PluginBuilder(name, version)
        .description(description)
        .author(author))

    if activate_fn:
        builder.on_activate(activate_fn)

    return builder.build()


__all__ = [
    'PluginBuilder',
    'CustomPlugin',
    'PluginConfig',
    'create_plugin',
]
