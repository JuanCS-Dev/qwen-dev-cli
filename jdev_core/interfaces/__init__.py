"""
Core Interfaces.

SCALE & SUSTAIN Phase 2.2 - Interface Extraction.

Defines abstract interfaces for dependency injection and testability.
All core components should implement these interfaces.

Usage:
    from jdev_core.interfaces import ILLMClient, IToolExecutor

    class MyLLMClient(ILLMClient):
        async def chat(self, message, context=None):
            ...

Author: JuanCS Dev
Date: 2025-11-26
"""

from .llm import ILLMClient, ILLMConfig, LLMResponse, LLMProvider, ChatMessage
from .tools import IToolExecutor, ITool, ToolResult, ToolCategory
from .agents import IAgentRouter, IAgent, AgentRouteResult
from .governance import IGovernance, RiskAssessment, RiskLevel
from .storage import IStorage, ICache, ICacheStats

__all__ = [
    # LLM
    'ILLMClient',
    'ILLMConfig',
    'LLMResponse',
    'LLMProvider',
    'ChatMessage',
    # Tools
    'IToolExecutor',
    'ITool',
    'ToolResult',
    'ToolCategory',
    # Agents
    'IAgentRouter',
    'IAgent',
    'AgentRouteResult',
    # Governance
    'IGovernance',
    'RiskAssessment',
    'RiskLevel',
    # Storage
    'IStorage',
    'ICache',
    'ICacheStats',
]
