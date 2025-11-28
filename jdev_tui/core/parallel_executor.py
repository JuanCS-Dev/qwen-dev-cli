"""
Parallel Executor - Tool Execution with Dependency Tracking
============================================================

Extracted from bridge.py for modularity.

Contains:
- ToolCallWithDeps: Tool call with dependency tracking
- ParallelExecutionResult: Result with timing metrics
- detect_tool_dependencies: Dependency detection
- ParallelToolExecutor: Wave-based parallel execution

Claude Code Parity: Independent tools execute in parallel,
dependent tools execute sequentially respecting dependencies.

Author: JuanCS Dev
Date: 2025-11-27
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ToolCallWithDeps:
    """
    Tool call with dependency tracking for parallel execution.

    Attributes:
        id: Unique identifier for this call
        tool_name: Name of the tool to execute
        args: Arguments for the tool
        depends_on: Set of call IDs this call depends on
    """
    id: str
    tool_name: str
    args: Dict[str, Any]
    depends_on: Set[str] = field(default_factory=set)


@dataclass
class ParallelExecutionResult:
    """
    Result of parallel tool execution with timing metrics.

    Attributes:
        results: Dict mapping call_id to execution result
        execution_time_ms: Total execution time in milliseconds
        parallelism_factor: >1.0 means parallel speedup achieved
        wave_count: Number of execution waves
    """
    results: Dict[str, Dict[str, Any]]
    execution_time_ms: float
    parallelism_factor: float
    wave_count: int


# =============================================================================
# DEPENDENCY DETECTION
# =============================================================================

def detect_tool_dependencies(tool_calls: List[Tuple[str, Dict]]) -> List[ToolCallWithDeps]:
    """
    Detect dependencies between tool calls using file-based heuristics.

    Dependency Rules (Claude Code pattern):
    - read_file() has no dependencies
    - write_file(path) depends on read_file(path) for same file
    - edit_file(path) depends on read_file(path) for same file
    - bash_command() depends on write_file() if command references the file
    - All tools that modify same file must be sequential
    - Git operations should be sequential

    Args:
        tool_calls: List of (tool_name, args) tuples

    Returns:
        List of ToolCallWithDeps with dependency graph

    Example:
        calls = [
            ("read_file", {"path": "foo.py"}),
            ("read_file", {"path": "bar.py"}),  # Can run in parallel with above
            ("edit_file", {"path": "foo.py", "...": "..."})  # Depends on first read
        ]
        deps = detect_tool_dependencies(calls)
        # deps[2].depends_on == {"tool_0"}
    """
    calls = []
    file_read_ops: Dict[str, str] = {}   # file_path -> call_id that read it
    file_write_ops: Dict[str, str] = {}  # file_path -> call_id that last wrote it

    # Tools that write to files
    WRITE_TOOLS = frozenset({
        "write_file",
        "edit_file",
        "delete_file",
        "insert_lines",
        "multi_edit",
        "create_directory",
        "move_file",
        "copy_file",
    })

    # Tools that read files
    READ_TOOLS = frozenset({
        "read_file",
        "read_multiple_files",
        "cat",
    })

    # Git tools (should be sequential)
    GIT_TOOLS = frozenset({
        "git_status",
        "git_diff",
        "git_commit",
        "git_log",
        "git_add",
        "git_push",
        "git_pull",
        "git_checkout",
        "git_branch",
    })

    for i, (tool_name, args) in enumerate(tool_calls):
        call_id = f"tool_{i}"
        depends_on: Set[str] = set()

        # Extract file path from various argument names
        file_path = (
            args.get("file_path")
            or args.get("path")
            or args.get("filepath")
            or args.get("notebook_path")
        )

        # Write operations depend on previous reads/writes to same file
        if tool_name in WRITE_TOOLS:
            if file_path:
                # Depend on any previous read of this file
                if file_path in file_read_ops:
                    depends_on.add(file_read_ops[file_path])
                # Depend on any previous write to this file
                if file_path in file_write_ops:
                    depends_on.add(file_write_ops[file_path])
                # Track this write
                file_write_ops[file_path] = call_id

        # Read operations depend on previous writes to same file
        elif tool_name in READ_TOOLS:
            if file_path and file_path in file_write_ops:
                depends_on.add(file_write_ops[file_path])
            # Track this read
            if file_path:
                file_read_ops[file_path] = call_id

        # Bash commands - check if they reference any written files
        elif tool_name == "bash_command":
            command = args.get("command", "")
            for written_file, dep_id in file_write_ops.items():
                if written_file in command:
                    depends_on.add(dep_id)

        # Git operations should be sequential
        elif tool_name in GIT_TOOLS:
            for prev_call in calls:
                if prev_call.tool_name in GIT_TOOLS:
                    depends_on.add(prev_call.id)

        calls.append(ToolCallWithDeps(
            id=call_id,
            tool_name=tool_name,
            args=args,
            depends_on=depends_on
        ))

    return calls


# =============================================================================
# PARALLEL EXECUTOR
# =============================================================================

# Type alias for tool executor function
ToolExecutorFn = Callable[[str, Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]]


class ParallelToolExecutor:
    """
    Execute tool calls with intelligent parallelization.

    Claude Code Pattern:
    - Independent tools execute in parallel (asyncio.gather)
    - Dependent tools execute sequentially (respecting dependencies)
    - Wave-based execution for optimal throughput

    Example:
        executor = ParallelToolExecutor(tools.execute_tool)
        result = await executor.execute([
            ("read_file", {"path": "a.py"}),
            ("read_file", {"path": "b.py"}),
            ("write_file", {"path": "c.py", "content": "..."})
        ])
        print(f"Executed in {result.wave_count} waves")
    """

    # Configuration
    MAX_PARALLEL_TOOLS = 5  # Max concurrent tool executions

    def __init__(self, execute_fn: ToolExecutorFn, max_parallel: int = None):
        """
        Initialize executor.

        Args:
            execute_fn: Async function to execute a single tool
            max_parallel: Max concurrent executions (default: 5)
        """
        self._execute_fn = execute_fn
        self._max_parallel = max_parallel or self.MAX_PARALLEL_TOOLS

    async def execute(
        self,
        tool_calls: List[Tuple[str, Dict[str, Any]]]
    ) -> ParallelExecutionResult:
        """
        Execute tool calls with intelligent parallelization.

        Args:
            tool_calls: List of (tool_name, args) tuples from ToolCallParser

        Returns:
            ParallelExecutionResult with all results and timing metrics
        """
        start_time = time.time()

        # Single tool - no parallelization needed
        if len(tool_calls) == 1:
            tool_name, args = tool_calls[0]
            result = await self._execute_fn(tool_name, **args)
            result["tool_name"] = tool_name
            return ParallelExecutionResult(
                results={"tool_0": result},
                execution_time_ms=(time.time() - start_time) * 1000,
                parallelism_factor=1.0,
                wave_count=1
            )

        # Detect dependencies
        calls_with_deps = detect_tool_dependencies(tool_calls)

        # Execute in waves
        results: Dict[str, Dict[str, Any]] = {}
        completed: Set[str] = set()
        wave_count = 0
        semaphore = asyncio.Semaphore(self._max_parallel)

        while len(completed) < len(calls_with_deps):
            # Find tools ready to execute (all dependencies completed)
            ready = [
                call for call in calls_with_deps
                if call.id not in completed
                and call.depends_on.issubset(completed)
            ]

            if not ready:
                # Circular dependency or error - break to avoid infinite loop
                logger.warning("Possible circular dependency detected")
                break

            wave_count += 1
            logger.debug(f"Wave {wave_count}: executing {len(ready)} tools")

            # Execute ready tools in parallel
            if len(ready) == 1:
                # Single tool in wave - direct execution
                call = ready[0]
                result = await self._execute_single(call, semaphore)
                results[call.id] = result
                completed.add(call.id)
            else:
                # Multiple tools - parallel execution
                tasks = [self._execute_single(call, semaphore) for call in ready]
                wave_results = await asyncio.gather(*tasks, return_exceptions=True)

                for call, item in zip(ready, wave_results):
                    if isinstance(item, Exception):
                        # Handle exception - create error result
                        logger.error(f"Tool {call.tool_name} failed: {item}")
                        results[call.id] = {
                            "success": False,
                            "error": str(item),
                            "tool_name": call.tool_name,
                            "execution_time_ms": 0
                        }
                    else:
                        results[call.id] = item
                    completed.add(call.id)

        # Calculate timing metrics
        total_time_ms = (time.time() - start_time) * 1000
        sequential_time = sum(
            r.get("execution_time_ms", 0)
            for r in results.values()
            if isinstance(r, dict)
        )
        parallelism_factor = sequential_time / total_time_ms if total_time_ms > 0 else 1.0

        return ParallelExecutionResult(
            results=results,
            execution_time_ms=total_time_ms,
            parallelism_factor=parallelism_factor,
            wave_count=wave_count
        )

    async def _execute_single(
        self,
        call: ToolCallWithDeps,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Execute a single tool with semaphore control."""
        async with semaphore:
            tool_start = time.time()
            try:
                result = await self._execute_fn(call.tool_name, **call.args)

                # Convert ToolResult to dict if needed
                if hasattr(result, 'success') and hasattr(result, 'data'):
                    # It's a ToolResult object
                    result_dict = {
                        "success": result.success,
                        "data": result.data,
                        "error": getattr(result, 'error', None),
                        "metadata": getattr(result, 'metadata', {})
                    }
                elif isinstance(result, dict):
                    result_dict = result
                else:
                    result_dict = {"success": True, "data": result}

                result_dict["tool_name"] = call.tool_name
                result_dict["execution_time_ms"] = (time.time() - tool_start) * 1000
                return result_dict
            except Exception as e:
                logger.error(f"Tool {call.tool_name} execution error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tool_name": call.tool_name,
                    "execution_time_ms": (time.time() - tool_start) * 1000
                }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ToolCallWithDeps",
    "ParallelExecutionResult",
    "detect_tool_dependencies",
    "ParallelToolExecutor",
]
