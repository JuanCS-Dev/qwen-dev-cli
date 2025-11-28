"""
Tool Result Formatter.

SCALE & SUSTAIN Phase 1.2.3 - CC Reduction.

Registry pattern for formatting tool execution results.
Reduces CC by replacing switch/if-else chains with O(1) lookup.

Author: JuanCS Dev
Date: 2025-11-26
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class OutputFormat(Enum):
    """Output format types."""
    PLAIN = "plain"
    RICH = "rich"
    JSON = "json"
    MARKDOWN = "markdown"


@dataclass
class FormattedResult:
    """Formatted tool result."""

    content: str
    format: OutputFormat = OutputFormat.PLAIN
    truncated: bool = False
    line_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return not self.content or self.content.strip() == ""


# Type alias for formatter functions
FormatterFunc = Callable[[Any, Dict[str, Any]], FormattedResult]


def format_bash_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format bash command result."""
    max_lines = options.get('max_lines', 100)

    if isinstance(result, dict):
        stdout = result.get('stdout', '')
        stderr = result.get('stderr', '')
        exit_code = result.get('exit_code', 0)

        lines = []
        if stdout:
            lines.extend(stdout.split('\n'))
        if stderr:
            lines.append(f"[stderr] {stderr}")
        if exit_code != 0:
            lines.append(f"[exit code: {exit_code}]")

        content = '\n'.join(lines)
    else:
        content = str(result)
        lines = content.split('\n')

    truncated = len(lines) > max_lines
    if truncated:
        content = '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        truncated=truncated,
        line_count=len(lines),
        metadata={'exit_code': result.get('exit_code', 0) if isinstance(result, dict) else 0}
    )


def format_file_content(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format file read result."""
    max_lines = options.get('max_lines', 200)
    show_line_numbers = options.get('line_numbers', True)

    if isinstance(result, dict):
        content = result.get('content', '')
        path = result.get('path', 'unknown')
    else:
        content = str(result)
        path = 'unknown'

    lines = content.split('\n')
    truncated = len(lines) > max_lines

    if truncated:
        lines = lines[:max_lines]

    if show_line_numbers:
        width = len(str(len(lines)))
        numbered_lines = [f"{i+1:>{width}}│ {line}" for i, line in enumerate(lines)]
        content = '\n'.join(numbered_lines)
    else:
        content = '\n'.join(lines)

    if truncated:
        content += f"\n... (truncated, showing {max_lines} of {len(lines)} lines)"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        truncated=truncated,
        line_count=len(lines),
        metadata={'path': path}
    )


def format_write_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format file write result."""
    if isinstance(result, dict):
        path = result.get('path', 'unknown')
        bytes_written = result.get('bytes_written', 0)
        success = result.get('success', True)

        if success:
            content = f"✓ Wrote {bytes_written} bytes to {path}"
        else:
            error = result.get('error', 'Unknown error')
            content = f"✗ Failed to write to {path}: {error}"
    else:
        content = str(result)

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        line_count=1
    )


def format_glob_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format glob/file search result."""
    max_files = options.get('max_files', 50)

    if isinstance(result, list):
        files = result
    elif isinstance(result, dict):
        files = result.get('files', [])
    else:
        files = [str(result)]

    truncated = len(files) > max_files
    display_files = files[:max_files]

    content = '\n'.join(display_files)
    if truncated:
        content += f"\n... ({len(files) - max_files} more files)"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        truncated=truncated,
        line_count=len(display_files),
        metadata={'total_files': len(files)}
    )


def format_grep_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format grep/search result."""
    max_matches = options.get('max_matches', 100)
    show_context = options.get('show_context', True)

    if isinstance(result, dict):
        matches = result.get('matches', [])
    elif isinstance(result, list):
        matches = result
    else:
        matches = [str(result)]

    truncated = len(matches) > max_matches
    display_matches = matches[:max_matches]

    lines = []
    for match in display_matches:
        if isinstance(match, dict):
            file_path = match.get('file', '')
            line_num = match.get('line', 0)
            content = match.get('content', '')
            lines.append(f"{file_path}:{line_num}: {content}")
        else:
            lines.append(str(match))

    content = '\n'.join(lines)
    if truncated:
        content += f"\n... ({len(matches) - max_matches} more matches)"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        truncated=truncated,
        line_count=len(lines),
        metadata={'total_matches': len(matches)}
    )


def format_json_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format JSON result."""
    import json

    indent = options.get('indent', 2)
    max_length = options.get('max_length', 10000)

    try:
        if isinstance(result, str):
            # Parse and re-format
            data = json.loads(result)
        else:
            data = result

        content = json.dumps(data, indent=indent, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        content = str(result)

    truncated = len(content) > max_length
    if truncated:
        content = content[:max_length] + "\n... (truncated)"

    return FormattedResult(
        content=content,
        format=OutputFormat.JSON,
        truncated=truncated,
        line_count=content.count('\n') + 1
    )


def format_error_result(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Format error result."""
    if isinstance(result, dict):
        error_type = result.get('type', 'Error')
        message = result.get('message', str(result))
        traceback = result.get('traceback', '')

        content = f"[{error_type}] {message}"
        if traceback and options.get('show_traceback', False):
            content += f"\n\nTraceback:\n{traceback}"
    elif isinstance(result, Exception):
        content = f"[{type(result).__name__}] {str(result)}"
    else:
        content = f"[Error] {str(result)}"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        line_count=content.count('\n') + 1,
        metadata={'is_error': True}
    )


def format_generic(result: Any, options: Dict[str, Any]) -> FormattedResult:
    """Generic formatter for unknown tool types."""
    max_length = options.get('max_length', 5000)

    if isinstance(result, dict):
        import json
        try:
            content = json.dumps(result, indent=2, ensure_ascii=False)
        except TypeError:
            content = str(result)
    elif isinstance(result, (list, tuple)):
        content = '\n'.join(str(item) for item in result)
    else:
        content = str(result)

    truncated = len(content) > max_length
    if truncated:
        content = content[:max_length] + "\n... (truncated)"

    return FormattedResult(
        content=content,
        format=OutputFormat.PLAIN,
        truncated=truncated,
        line_count=content.count('\n') + 1
    )


class ToolResultFormatter:
    """
    Registry-based tool result formatter.

    Replaces complex if/elif chains with O(1) dictionary lookup.
    CC reduction: -10 to -12 points.

    Usage:
        formatter = ToolResultFormatter()
        result = formatter.format('bash', tool_output)
        print(result.content)
    """

    # Default formatters registry
    _default_formatters: Dict[str, FormatterFunc] = {
        'bash': format_bash_result,
        'shell': format_bash_result,
        'execute': format_bash_result,
        'run_command': format_bash_result,
        'read_file': format_file_content,
        'read': format_file_content,
        'cat': format_file_content,
        'write_file': format_write_result,
        'write': format_write_result,
        'edit': format_write_result,
        'glob': format_glob_result,
        'find': format_glob_result,
        'list_files': format_glob_result,
        'grep': format_grep_result,
        'search': format_grep_result,
        'ripgrep': format_grep_result,
        'json': format_json_result,
        'parse_json': format_json_result,
        'error': format_error_result,
        'exception': format_error_result,
    }

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize formatter with options.

        Args:
            options: Default formatting options
        """
        self._formatters = dict(self._default_formatters)
        self._options = options or {}

    def register(self, tool_name: str, formatter: FormatterFunc) -> None:
        """
        Register a custom formatter for a tool.

        Args:
            tool_name: Name of the tool
            formatter: Formatter function
        """
        self._formatters[tool_name] = formatter

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a formatter.

        Args:
            tool_name: Name of the tool

        Returns:
            True if unregistered, False if not found
        """
        if tool_name in self._formatters:
            del self._formatters[tool_name]
            return True
        return False

    def format(
        self,
        tool_name: str,
        result: Any,
        options: Optional[Dict[str, Any]] = None
    ) -> FormattedResult:
        """
        Format a tool result.

        Args:
            tool_name: Name of the tool
            result: Tool execution result
            options: Formatting options (overrides defaults)

        Returns:
            FormattedResult with formatted content
        """
        # Merge options
        merged_options = {**self._options, **(options or {})}

        # Get formatter (O(1) lookup)
        formatter = self._formatters.get(tool_name, format_generic)

        try:
            return formatter(result, merged_options)
        except Exception as e:
            # Fallback on formatter error
            return FormattedResult(
                content=f"[Formatting error for {tool_name}] {str(e)}\n\nRaw result: {result}",
                format=OutputFormat.PLAIN,
                metadata={'formatting_error': str(e)}
            )

    @property
    def registered_tools(self) -> List[str]:
        """Get list of tools with registered formatters."""
        return list(self._formatters.keys())


# Global formatter instance
_global_formatter: Optional[ToolResultFormatter] = None


def get_formatter() -> ToolResultFormatter:
    """Get global formatter instance."""
    global _global_formatter
    if _global_formatter is None:
        _global_formatter = ToolResultFormatter()
    return _global_formatter


def register_formatter(tool_name: str, formatter: FormatterFunc) -> None:
    """Register a formatter in the global registry."""
    get_formatter().register(tool_name, formatter)


def format_result(
    tool_name: str,
    result: Any,
    options: Optional[Dict[str, Any]] = None
) -> FormattedResult:
    """Format a result using the global formatter."""
    return get_formatter().format(tool_name, result, options)


__all__ = [
    'ToolResultFormatter',
    'FormattedResult',
    'OutputFormat',
    'FormatterFunc',
    'register_formatter',
    'format_result',
    'get_formatter',
    # Individual formatters for extension
    'format_bash_result',
    'format_file_content',
    'format_write_result',
    'format_glob_result',
    'format_grep_result',
    'format_json_result',
    'format_error_result',
    'format_generic',
]
