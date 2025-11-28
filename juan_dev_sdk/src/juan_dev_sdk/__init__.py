"""
Juan Dev SDK.

SDK for building extensions and integrations with Juan Dev Code.

SCALE & SUSTAIN Phase 2.3 - SDK Initial Structure.

Usage:
    from juan_dev_sdk import JuanDevClient

    async with JuanDevClient() as client:
        async for chunk in client.chat("explain this code"):
            print(chunk, end="")

Author: JuanCS Dev
Date: 2025-11-26
"""

from .client import JuanDevClient
from .agents import create_agent, AgentBuilder
from .tools import create_tool, ToolBuilder
from .plugins import create_plugin, PluginBuilder
from .types import (
    Message,
    ToolCall,
    AgentResponse,
    SDKConfig,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    'JuanDevClient',
    # Builders
    'create_agent',
    'AgentBuilder',
    'create_tool',
    'ToolBuilder',
    'create_plugin',
    'PluginBuilder',
    # Types
    'Message',
    'ToolCall',
    'AgentResponse',
    'SDKConfig',
]
