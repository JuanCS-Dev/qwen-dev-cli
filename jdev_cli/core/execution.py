"""
jdev_cli.core.execution: Canonical ExecutionResult Definition.

This module provides the SINGLE source of truth for ExecutionResult.
All other modules should import from here.

Usage:
    from jdev_cli.core.execution import ExecutionResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ExecutionResult:
    """
    Result of command/code execution.

    This is the canonical definition used across all jdev packages.

    Attributes:
        success: Whether execution completed without error
        exit_code: Process exit code (0 = success)
        stdout: Standard output content
        stderr: Standard error content
        timed_out: Whether execution was terminated due to timeout
        resource_exceeded: Whether resource limits were exceeded
        execution_time: Time taken in seconds
        command: The command that was executed
        working_directory: Directory where command was run
        error_message: Human-readable error description
        block_reason: Reason for blocking (if blocked)
    """
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    resource_exceeded: bool = False
    execution_time: float = 0.0
    command: List[str] = field(default_factory=list)
    working_directory: Optional[str] = None
    error_message: Optional[str] = None
    block_reason: Optional[str] = None
    output_truncated: bool = False

    @property
    def blocked(self) -> bool:
        """Check if execution was blocked by security policy."""
        return self.block_reason is not None or (
            not self.success and
            self.error_message is not None and
            any(kw in self.error_message.lower() for kw in ["blocked", "validation failed", "not allowed", "permission"])
        )

    @classmethod
    def failure(cls, error: str, command: Optional[List[str]] = None) -> "ExecutionResult":
        """Create a failed execution result."""
        return cls(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=error,
            command=command or [],
            error_message=error
        )

    @classmethod
    def success_result(
        cls,
        stdout: str = "",
        stderr: str = "",
        command: Optional[List[str]] = None,
        execution_time: float = 0.0
    ) -> "ExecutionResult":
        """Create a successful execution result."""
        return cls(
            success=True,
            exit_code=0,
            stdout=stdout,
            stderr=stderr,
            command=command or [],
            execution_time=execution_time
        )

    @property
    def output(self) -> str:
        """Combined stdout and stderr for compatibility."""
        if self.stdout and self.stderr:
            return f"{self.stdout}\n{self.stderr}"
        return self.stdout or self.stderr or ""

    @property
    def error(self) -> Optional[str]:
        """Error message or stderr for compatibility."""
        return self.error_message or (self.stderr if not self.success else None)


__all__ = ['ExecutionResult']
