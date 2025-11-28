"""
Juan-Dev-Code Gradio UI Package.

Hackathon Day 30 - Gradio 6 + GeminiClient Integration.

Exports:
- create_ui: Factory function to create the Gradio Blocks UI
- GradioStreamingBridge: Bridge between GeminiClient and Gradio
- ChatMessage: Gradio 6 compatible message dataclass
"""

from .app import create_ui
from .streaming_bridge import (
    GradioStreamingBridge,
    ChatMessage,
    StreamingMetrics,
    create_streaming_bridge,
)

__all__ = [
    "create_ui",
    "GradioStreamingBridge",
    "ChatMessage",
    "StreamingMetrics",
    "create_streaming_bridge",
]
