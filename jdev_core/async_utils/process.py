"""
Async Process Execution.

SCALE & SUSTAIN Phase 3.1 - Async Everywhere.

Async wrappers for subprocess execution using asyncio.subprocess.

Author: JuanCS Dev
Date: 2025-11-26
"""

import asyncio
import shlex
from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class ProcessResult:
    """Result of a process execution."""

    returncode: int
    stdout: str
    stderr: str
    command: str

    @property
    def success(self) -> bool:
        """Check if process succeeded."""
        return self.returncode == 0

    @property
    def output(self) -> str:
        """Combined stdout and stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return '\n'.join(parts)


async def run_command(
    command: Union[str, List[str]],
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    shell: bool = False,
    capture_output: bool = True
) -> ProcessResult:
    """
    Run a command asynchronously.

    Args:
        command: Command string or list of arguments
        cwd: Working directory
        env: Environment variables
        timeout: Timeout in seconds
        shell: Run through shell
        capture_output: Capture stdout/stderr

    Returns:
        ProcessResult with output and return code
    """
    if isinstance(command, str) and not shell:
        args = shlex.split(command)
    elif isinstance(command, list):
        args = command
        command = ' '.join(command)
    else:
        args = command

    if shell:
        process = await asyncio.create_subprocess_shell(
            command if isinstance(command, str) else ' '.join(args),
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None,
            cwd=cwd,
            env=env
        )
    else:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None,
            cwd=cwd,
            env=env
        )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return ProcessResult(
            returncode=-1,
            stdout='',
            stderr=f'Process timed out after {timeout} seconds',
            command=command if isinstance(command, str) else ' '.join(args)
        )

    stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ''
    stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ''

    return ProcessResult(
        returncode=process.returncode or 0,
        stdout=stdout.strip(),
        stderr=stderr.strip(),
        command=command if isinstance(command, str) else ' '.join(args)
    )


async def run_shell(
    script: str,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None
) -> ProcessResult:
    """
    Run a shell script asynchronously.

    Args:
        script: Shell script to execute
        cwd: Working directory
        env: Environment variables
        timeout: Timeout in seconds

    Returns:
        ProcessResult with output and return code
    """
    return await run_command(
        script,
        cwd=cwd,
        env=env,
        timeout=timeout,
        shell=True
    )


async def run_many(
    commands: List[Union[str, List[str]]],
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    fail_fast: bool = False
) -> List[ProcessResult]:
    """
    Run multiple commands concurrently.

    Args:
        commands: List of commands to run
        cwd: Working directory for all commands
        env: Environment variables
        timeout: Timeout per command
        fail_fast: Stop on first failure

    Returns:
        List of ProcessResults
    """
    if fail_fast:
        results = []
        for cmd in commands:
            result = await run_command(cmd, cwd=cwd, env=env, timeout=timeout)
            results.append(result)
            if not result.success:
                break
        return results
    else:
        tasks = [
            run_command(cmd, cwd=cwd, env=env, timeout=timeout)
            for cmd in commands
        ]
        return await asyncio.gather(*tasks)


__all__ = [
    'ProcessResult',
    'run_command',
    'run_shell',
    'run_many',
]
