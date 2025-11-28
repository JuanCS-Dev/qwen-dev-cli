"""
Tool Result Formatters.

SCALE & SUSTAIN Phase 1.2.3 - CC Reduction.

Registry-based formatters for tool execution results.

Author: JuanCS Dev
Date: 2025-11-26
"""

from .tool_formatter import (
    ToolResultFormatter,
    FormattedResult,
    register_formatter,
    format_result,
)

__all__ = [
    'ToolResultFormatter',
    'FormattedResult',
    'register_formatter',
    'format_result',
]
