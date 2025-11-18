"""Intelligence layer for qwen-dev-cli.

Architecture:
- types.py: Type definitions (Boris Cherny: types first!)
- engine.py: Core suggestion engine
- patterns.py: Built-in suggestion patterns
"""

from .types import (
    Suggestion,
    SuggestionType,
    SuggestionConfidence,
    Context,
    SuggestionPattern,
    SuggestionResult
)

__all__ = [
    'Suggestion',
    'SuggestionType',
    'SuggestionConfidence',
    'Context',
    'SuggestionPattern',
    'SuggestionResult'
]
