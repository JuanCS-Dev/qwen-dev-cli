"""
Tool Builder.

SCALE & SUSTAIN Phase 2.3 - SDK Tool Creation.

Helpers for creating custom tools.

Author: JuanCS Dev
Date: 2025-11-26
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, Any, List, Optional
from enum import Enum


class ToolCategory(Enum):
    """Tool categories."""
    FILE = "file"
    GIT = "git"
    SHELL = "shell"
    SEARCH = "search"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class ToolParam:
    """Tool parameter definition."""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = False
    default: Any = None


@dataclass
class ToolConfig:
    """Tool configuration."""
    name: str
    description: str
    category: ToolCategory = ToolCategory.CUSTOM
    parameters: List[ToolParam] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolBuilder:
    """
    Builder for creating custom tools.

    Usage:
        tool = (ToolBuilder("my_tool")
            .description("Does something useful")
            .param("input", "string", "The input value", required=True)
            .on_execute(my_execute_fn)
            .build())
    """

    def __init__(self, name: str):
        """Initialize builder with tool name."""
        self._config = ToolConfig(name=name, description="")
        self._execute_fn: Optional[Callable] = None

    def description(self, desc: str) -> 'ToolBuilder':
        """Set tool description."""
        self._config.description = desc
        return self

    def category(self, cat: ToolCategory) -> 'ToolBuilder':
        """Set tool category."""
        self._config.category = cat
        return self

    def param(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = False,
        default: Any = None
    ) -> 'ToolBuilder':
        """Add a parameter."""
        self._config.parameters.append(ToolParam(
            name=name,
            type=type,
            description=description,
            required=required,
            default=default
        ))
        return self

    def metadata(self, **kwargs) -> 'ToolBuilder':
        """Add metadata."""
        self._config.metadata.update(kwargs)
        return self

    def on_execute(self, fn: Callable) -> 'ToolBuilder':
        """Set execute handler."""
        self._execute_fn = fn
        return self

    def build(self) -> 'CustomTool':
        """Build the tool."""
        if not self._config.description:
            raise ValueError("Tool description is required")
        if not self._execute_fn:
            raise ValueError("Execute handler is required")
        return CustomTool(self._config, self._execute_fn)


@dataclass
class ToolResult:
    """Tool execution result."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: Dict[str, Any] = None) -> 'ToolResult':
        return cls(success=True, data=data or {})

    @classmethod
    def fail(cls, error: str) -> 'ToolResult':
        return cls(success=False, error=error)


class CustomTool:
    """Custom tool created via builder."""

    def __init__(self, config: ToolConfig, execute_fn: Callable):
        self.config = config
        self._execute_fn = execute_fn

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description

    @property
    def category(self) -> ToolCategory:
        return self.config.category

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for parameters."""
        properties = {}
        required = []

        for param in self.config.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.default is not None:
                properties[param.name]["default"] = param.default
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }

    async def execute(self, **params) -> ToolResult:
        """Execute the tool."""
        try:
            # Validate required params
            for param in self.config.parameters:
                if param.required and param.name not in params:
                    return ToolResult.fail(f"Missing required parameter: {param.name}")
                if param.name not in params and param.default is not None:
                    params[param.name] = param.default

            # Execute handler
            result = self._execute_fn(**params)

            # Handle async
            if hasattr(result, '__await__'):
                result = await result

            # Wrap result
            if isinstance(result, ToolResult):
                return result
            elif isinstance(result, dict):
                return ToolResult.ok(result)
            else:
                return ToolResult.ok({"result": result})

        except Exception as e:
            return ToolResult.fail(str(e))


def create_tool(
    name: str,
    description: str,
    execute_fn: Callable,
    category: ToolCategory = ToolCategory.CUSTOM,
) -> CustomTool:
    """
    Create a custom tool.

    Shorthand for ToolBuilder.

    Args:
        name: Tool name
        description: Tool description
        execute_fn: Execute handler
        category: Tool category

    Returns:
        Custom tool instance
    """
    return (ToolBuilder(name)
        .description(description)
        .category(category)
        .on_execute(execute_fn)
        .build())


__all__ = [
    'ToolBuilder',
    'CustomTool',
    'ToolConfig',
    'ToolParam',
    'ToolResult',
    'ToolCategory',
    'create_tool',
]
