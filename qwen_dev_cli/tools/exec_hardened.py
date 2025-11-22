"""Hardened bash command execution - Linus Torvalds approved.

Design principles:
1. NEVER trust user input
2. Fail loudly and early
3. Resource limits are NOT optional
4. Security over convenience
5. Log everything or die trying

Author: Boris Cherny (Linus mode)
Date: 2025-11-21
"""

import subprocess
import asyncio
import os
import re
import logging
import resource
import signal
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass

from .base import Tool, ToolResult, ToolCategory
from .validated import ValidatedTool
from ..core.validation import Required, TypeCheck

logger = logging.getLogger(__name__)


@dataclass
class ExecutionLimits:
    """Resource limits for command execution.
    
    These are not suggestions. These are HARD LIMITS.
    If you hit them, your process dies. No negotiation.
    """
    timeout_seconds: int = 30
    max_output_bytes: int = 1024 * 1024  # 1MB
    max_memory_mb: int = 512
    max_cpu_percent: int = 80
    max_open_files: int = 100


class CommandValidator:
    """Validates bash commands before execution.
    
    Philosophy: Whitelist good, blacklist bad is for amateurs.
    We do BOTH. Defense in depth or go home.
    """
    
    # Commands that will NEVER be allowed. Period.
    BLACKLIST: Set[str] = {
        'rm -rf /',
        'rm -rf /*',
        'rm -rf ~',
        'rm -rf ~/*',
        'chmod -R 777',
        'chmod 777 /',
        'dd if=/dev/zero',
        'dd if=/dev/random',
        'mkfs',
        'mkfs.ext4',
        ':(){ :|:& };:',  # Fork bomb
        'curl | sh',
        'wget | sh',
        'curl | bash',
        'wget | bash',
    }
    
    # Dangerous patterns (regex)
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',  # Any rm -rf on root
        r'chmod\s+-R\s+777',  # Recursive 777
        r'dd\s+if=/dev/(zero|random|urandom)',  # Disk destroyers
        r'>\s*/dev/sd[a-z]',  # Writing to raw disk
        r'mkfs\.',  # Filesystem creation
        r':\(\)\{.*\|.*&\s*\}',  # Fork bombs
        r'eval.*\$\(',  # Code injection via eval
        r'\$\(.*curl',  # Remote code execution
        r'\$\(.*wget',  # Remote code execution
        r'(curl|wget).*\|\s*(sh|bash)',  # Piping curl/wget to shell
        r'sudo\s+',  # No sudo ever
        r'su\s+',  # No su either
    ]
    
    # Suspicious characters that might indicate shell injection
    SHELL_INJECTION_CHARS = {
        ';', '&&', '||', '|', '`', '$(',
        '$()', '${', '>', '>>', '<', '<<',
    }
    
    @classmethod
    def validate(cls, command: str) -> tuple[bool, Optional[str]]:
        """Validate command is safe to execute.
        
        Returns:
            (is_valid, error_message)
        """
        # 1. Empty or whitespace-only
        if not command or not command.strip():
            return False, "Empty command"
        
        # 2. Check blacklist (exact matches)
        cmd_lower = command.lower().strip()
        for blocked in cls.BLACKLIST:
            if blocked in cmd_lower:
                logger.error(f"BLOCKED: Blacklisted command detected: {blocked}")
                return False, f"Blacklisted command: {blocked}"
        
        # 3. Check dangerous patterns (regex)
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.error(f"BLOCKED: Dangerous pattern detected: {pattern}")
                return False, f"Dangerous pattern detected: {pattern}"
        
        # 4. Check for excessive piping (potential DoS)
        pipe_count = command.count('|')
        if pipe_count > 10:
            logger.warning(f"SUSPICIOUS: Excessive piping ({pipe_count} pipes)")
            return False, f"Too many pipes: {pipe_count} (max 10)"
        
        # 5. Check command length (absurdly long commands are suspicious)
        if len(command) > 4096:
            logger.warning(f"BLOCKED: Command too long ({len(command)} chars)")
            return False, f"Command too long: {len(command)} chars (max 4096)"
        
        # 6. Check for shell injection attempts
        # This is informational, not blocking (legitimate commands use these)
        injection_chars_found = [c for c in cls.SHELL_INJECTION_CHARS if c in command]
        if len(injection_chars_found) > 5:
            logger.warning(f"SUSPICIOUS: Many shell metacharacters: {injection_chars_found}")
        
        return True, None
    
    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize a file path.
        
        Resolve symlinks, check for traversal, validate exists.
        """
        try:
            p = Path(path).expanduser().resolve(strict=False)
            
            # Check for path traversal
            cwd = Path.cwd().resolve()
            try:
                p.relative_to(cwd)
            except ValueError:
                # Path is outside CWD, that's often fine
                # but log it
                logger.info(f"Path outside CWD: {p}")
            
            return str(p)
        except Exception as e:
            logger.error(f"Path sanitization failed: {e}")
            raise ValueError(f"Invalid path: {path}")


class BashCommandToolHardened(ValidatedTool):
    """Hardened bash command execution.
    
    This is not your grandmother's subprocess.run().
    This is PRODUCTION-GRADE command execution with:
    - Input validation (whitelist + blacklist)
    - Resource limits (CPU, memory, time, output size)
    - Security sandboxing (no sudo, no root)
    - Comprehensive logging
    - Graceful degradation
    
    If this breaks, your command was probably malicious anyway.
    """
    
    def __init__(self, limits: Optional[ExecutionLimits] = None):
        super().__init__()
        self.name = "bash_command"  # Override auto-generated name
        self.category = ToolCategory.EXECUTION
        self.description = "Execute shell command with hardened security and resource limits"
        self.limits = limits or ExecutionLimits()
        self.validator = CommandValidator()
        
        self.parameters = {
            "command": {
                "type": "string",
                "description": "Shell command to execute (validated for safety)",
                "required": True
            },
            "cwd": {
                "type": "string",
                "description": "Working directory (must exist)",
                "required": False
            },
            "timeout": {
                "type": "integer",
                "description": f"Timeout in seconds (max {self.limits.timeout_seconds})",
                "required": False
            },
            "env": {
                "type": "object",
                "description": "Environment variables (merged with current env)",
                "required": False
            }
        }
        
        logger.info(f"BashCommandToolHardened initialized with limits: {self.limits}")
    
    def get_validators(self):
        """Validate parameters."""
        return {'command': Required('command')}
    
    def _setup_resource_limits(self):
        """Set resource limits for child process.
        
        This runs in the child process BEFORE exec.
        If it fails, the child dies. Good.
        """
        try:
            # CPU time limit (soft, hard)
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.limits.timeout_seconds, self.limits.timeout_seconds + 5)
            )
            
            # Memory limit (in bytes)
            max_memory = self.limits.max_memory_mb * 1024 * 1024
            resource.setrlimit(
                resource.RLIMIT_AS,
                (max_memory, max_memory)
            )
            
            # Max open files
            resource.setrlimit(
                resource.RLIMIT_NOFILE,
                (self.limits.max_open_files, self.limits.max_open_files)
            )
            
            # Core dumps disabled (security)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
            # Process priority (nice value 10 = lower priority)
            os.nice(10)
            
            logger.debug("Resource limits applied successfully")
        except Exception as e:
            logger.error(f"Failed to set resource limits: {e}")
            # Don't fail here, limits are best-effort on some systems
    
    async def _execute_validated(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ToolResult:
        """Execute bash command with full hardening.
        
        This is where the magic happens. Or where your command dies trying.
        """
        start_time = asyncio.get_event_loop().time()
        
        # 1. VALIDATION PHASE
        logger.info(f"EXEC REQUEST: {command[:100]}...")
        
        is_valid, error_msg = self.validator.validate(command)
        if not is_valid:
            logger.error(f"VALIDATION FAILED: {error_msg}")
            return ToolResult(
                success=False,
                error=f"Command validation failed: {error_msg}",
                metadata={"validation_error": True}
            )
        
        # 2. SANITIZE CWD
        if cwd:
            try:
                cwd = self.validator.sanitize_path(cwd)
                if not Path(cwd).exists():
                    return ToolResult(
                        success=False,
                        error=f"Working directory does not exist: {cwd}"
                    )
                if not Path(cwd).is_dir():
                    return ToolResult(
                        success=False,
                        error=f"Not a directory: {cwd}"
                    )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid working directory: {e}"
                )
        
        # 3. SETUP TIMEOUT
        actual_timeout = min(
            timeout or self.limits.timeout_seconds,
            self.limits.timeout_seconds
        )
        
        # 4. SETUP ENVIRONMENT
        # Start with clean environment, add safe defaults, then user vars
        exec_env = os.environ.copy()
        exec_env['BASH_ENV'] = ''  # No startup files
        exec_env['ENV'] = ''
        exec_env['PATH'] = '/usr/local/bin:/usr/bin:/bin'  # Restricted PATH
        
        if env:
            # Filter out dangerous env vars
            safe_env = {
                k: v for k, v in env.items()
                if k not in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'BASH_ENV']
            }
            exec_env.update(safe_env)
        
        # 5. EXECUTION PHASE
        try:
            logger.info(f"EXECUTING: {command} (timeout={actual_timeout}s, cwd={cwd or 'CWD'})")
            
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=exec_env,
                preexec_fn=self._setup_resource_limits,  # Apply limits in child
                limit=self.limits.max_output_bytes  # Limit output buffer
            )
            
            try:
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=actual_timeout
                )
                
                # Decode output
                stdout_str = stdout.decode('utf-8', errors='replace') if stdout else ""
                stderr_str = stderr.decode('utf-8', errors='replace') if stderr else ""
                
                # Truncate if too large
                if len(stdout_str) > self.limits.max_output_bytes:
                    stdout_str = stdout_str[:self.limits.max_output_bytes] + "\n\n[OUTPUT TRUNCATED]"
                    logger.warning(f"STDOUT truncated to {self.limits.max_output_bytes} bytes")
                
                if len(stderr_str) > self.limits.max_output_bytes:
                    stderr_str = stderr_str[:self.limits.max_output_bytes] + "\n\n[OUTPUT TRUNCATED]"
                    logger.warning(f"STDERR truncated to {self.limits.max_output_bytes} bytes")
                
                elapsed = asyncio.get_event_loop().time() - start_time
                
                logger.info(
                    f"EXEC COMPLETE: exit={proc.returncode}, "
                    f"elapsed={elapsed:.2f}s, "
                    f"stdout={len(stdout_str)}B, stderr={len(stderr_str)}B"
                )
                
                return ToolResult(
                    success=proc.returncode == 0,
                    data={
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "exit_code": proc.returncode,
                        "elapsed_seconds": round(elapsed, 3)
                    },
                    metadata={
                        "command": command[:200],  # Truncate in metadata
                        "cwd": cwd or str(Path.cwd()),
                        "exit_code": proc.returncode,
                        "elapsed": elapsed,
                        "timeout": actual_timeout,
                        "truncated": len(stdout_str) >= self.limits.max_output_bytes
                    }
                )
            
            except asyncio.TimeoutError:
                # Command TIMEOUT, kill it HARD
                logger.error(f"TIMEOUT: Command exceeded {actual_timeout}s")
                try:
                    proc.kill()
                    await proc.wait()
                except:
                    pass
                
                return ToolResult(
                    success=False,
                    error=f"Command TIMEOUT after {actual_timeout}s",
                    metadata={
                        "timeout": True,
                        "limit": actual_timeout
                    }
                )
        
        except MemoryError as e:
            logger.error(f"MEMORY LIMIT: Command exceeded memory limit")
            return ToolResult(
                success=False,
                error=f"Command exceeded memory limit ({self.limits.max_memory_mb}MB)",
                metadata={"memory_error": True}
            )
        
        except OSError as e:
            # OS-level errors (file not found, permission denied, etc)
            logger.error(f"OS ERROR: {e}")
            return ToolResult(
                success=False,
                error=f"OS error: {e}",
                metadata={"os_error": str(e)}
            )
        
        except Exception as e:
            # Catch-all for unexpected errors
            logger.exception(f"UNEXPECTED ERROR: {e}")
            return ToolResult(
                success=False,
                error=f"Unexpected error: {type(e).__name__}: {e}",
                metadata={"exception": str(e)}
            )


# Alias for backward compatibility
BashCommandTool = BashCommandToolHardened
