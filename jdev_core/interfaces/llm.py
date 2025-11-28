"""
LLM Client Interface.

SCALE & SUSTAIN Phase 2.2 - Interface Extraction.

Defines the interface for LLM clients to enable:
- Multiple provider support (Gemini, OpenAI, Anthropic, local)
- Dependency injection for testing
- Consistent API across implementations

Author: JuanCS Dev
Date: 2025-11-26
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator, Optional, Dict, Any, List
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class ILLMConfig:
    """Configuration for LLM clients."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0
    retry_attempts: int = 3
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        """Check if response completed normally."""
        return self.finish_reason in (None, "stop", "end_turn")


@dataclass
class ChatMessage:
    """Chat message for conversation context."""
    role: str  # user, assistant, system
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ILLMClient(ABC):
    """
    Interface for LLM clients.

    All LLM implementations must implement this interface.

    Example:
        class GeminiClient(ILLMClient):
            async def chat(self, message, context=None):
                async for chunk in self._stream_response(message):
                    yield chunk

            async def complete(self, prompt):
                response = await self._generate(prompt)
                return response.text
    """

    @abstractmethod
    async def chat(
        self,
        message: str,
        context: Optional[List[ChatMessage]] = None,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream chat response.

        Args:
            message: User message
            context: Previous conversation messages
            system_prompt: Optional system prompt override

        Yields:
            Response text chunks
        """
        pass

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """
        Get completion (non-streaming).

        Args:
            prompt: Prompt text
            **kwargs: Additional parameters

        Returns:
            Complete response
        """
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Generate text (simple interface).

        Args:
            prompt: Prompt text
            **kwargs: Additional parameters

        Returns:
            Generated text string
        """
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if client is connected and ready."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get current model name."""
        pass

    @property
    @abstractmethod
    def provider(self) -> LLMProvider:
        """Get provider type."""
        pass

    # ========== Optional Methods ==========

    async def health_check(self) -> bool:
        """
        Check if LLM service is healthy.

        Default implementation checks is_connected.
        """
        return self.is_connected

    def get_token_count(self, text: str) -> int:
        """
        Estimate token count for text.

        Default implementation uses rough estimate.
        Override for accurate counting.
        """
        # Rough estimate: ~4 chars per token
        return len(text) // 4

    async def close(self) -> None:
        """
        Close client connections.

        Override if cleanup needed.
        """
        pass


__all__ = [
    'ILLMClient',
    'ILLMConfig',
    'LLMResponse',
    'LLMProvider',
    'ChatMessage',
]
