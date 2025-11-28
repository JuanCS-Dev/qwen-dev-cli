"""
PROMETHEUS Streaming Bridge for Gradio UI.

Provides streaming integration between Gradio and PROMETHEUS.
"""

import asyncio
from typing import AsyncIterator, Optional, Dict, Any, List, Iterator
from dataclasses import dataclass

from jdev_cli.core.providers.prometheus_provider import PrometheusProvider, PrometheusConfig


@dataclass
class PrometheusUIConfig:
    """Configuration for PROMETHEUS UI integration."""
    enable_world_model: bool = True
    enable_memory: bool = True
    enable_reflection: bool = True
    show_thinking: bool = True
    show_memory_context: bool = True
    timeout: float = 120.0


class PrometheusStreamingBridge:
    """
    Streaming bridge for PROMETHEUS in Gradio UI.

    Provides:
    - Streaming responses with progress indicators
    - Memory status updates
    - World model simulation previews
    - Evolution controls
    """

    def __init__(self, config: Optional[PrometheusUIConfig] = None):
        self.config = config or PrometheusUIConfig()
        self._provider: Optional[PrometheusProvider] = None
        self._initialized = False
        self._conversation_history: List[Dict[str, str]] = []

    async def _ensure_provider(self):
        """Lazy initialization."""
        if not self._initialized:
            prometheus_config = PrometheusConfig(
                enable_world_model=self.config.enable_world_model,
                enable_memory=self.config.enable_memory,
                enable_reflection=self.config.enable_reflection,
            )
            self._provider = PrometheusProvider(config=prometheus_config)
            await self._provider._ensure_initialized()
            self._initialized = True

    def stream(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Iterator[str]:
        """
        Stream response from PROMETHEUS (sync wrapper for Gradio).

        Args:
            message: User message
            history: Conversation history

        Yields:
            Response chunks
        """
        # Run async in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            async def _stream():
                await self._ensure_provider()

                # Build context from history
                context = history or self._conversation_history

                # Stream response
                full_response = ""
                async for chunk in self._provider.stream(
                    prompt=message,
                    context=context
                ):
                    full_response += chunk
                    yield chunk

                # Update history
                self._conversation_history.append({"role": "user", "content": message})
                self._conversation_history.append({"role": "assistant", "content": full_response})

            # Convert async generator to sync
            gen = _stream()
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    async def stream_async(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        """
        Async stream response from PROMETHEUS.

        Args:
            message: User message
            history: Conversation history

        Yields:
            Response chunks
        """
        await self._ensure_provider()

        context = history or self._conversation_history

        full_response = ""
        async for chunk in self._provider.stream(
            prompt=message,
            context=context
        ):
            full_response += chunk
            yield chunk

        self._conversation_history.append({"role": "user", "content": message})
        self._conversation_history.append({"role": "assistant", "content": full_response})

    def get_prometheus_status(self) -> Dict[str, Any]:
        """Get PROMETHEUS system status for dashboard."""
        if not self._initialized or not self._provider:
            return {
                "status": "not_initialized",
                "memory": {},
                "world_model": {},
                "evolution": {},
            }

        base_status = self._provider.get_status()

        # Extract component statuses
        return {
            "status": "active",
            "memory": base_status.get("memory", {}),
            "world_model": base_status.get("world_model", {}),
            "evolution": base_status.get("evolution", {}),
            "total_interactions": len(self._conversation_history) // 2,
        }

    async def evolve(self, iterations: int = 5) -> Dict[str, Any]:
        """Run evolution cycle."""
        await self._ensure_provider()
        return await self._provider.evolve(iterations)

    async def query_memory(self, query: str) -> Dict[str, Any]:
        """Query PROMETHEUS memory."""
        await self._ensure_provider()
        return self._provider.get_memory_context(query)

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self._conversation_history.copy()
