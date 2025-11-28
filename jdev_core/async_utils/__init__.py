"""
Async Utilities.

SCALE & SUSTAIN Phase 3.1 - Async Everywhere.

Provides async wrappers and utilities for:
- File I/O (aiofiles)
- Process execution (asyncio subprocess)
- HTTP requests (httpx)
- Concurrency utilities (semaphores, retry, timeout)

Author: JuanCS Dev
Date: 2025-11-26
"""

from .files import (
    read_file,
    write_file,
    read_json,
    write_json,
    file_exists,
    list_dir,
    read_bytes,
    write_bytes,
    AIOFILES_AVAILABLE,
)

from .process import (
    run_command,
    run_shell,
    run_many,
    ProcessResult,
)

from .http import (
    HttpClient,
    HttpResponse,
    HttpError,
    get,
    post,
    HTTP_CLIENT,
)

from .utils import (
    run_sync,
    gather_with_limit,
    timeout,
    timeout_or_raise,
    TimeoutError,
    retry,
    retry_async,
    first_completed,
    debounce,
    AsyncLock,
)

__all__ = [
    # Files
    'read_file',
    'write_file',
    'read_json',
    'write_json',
    'file_exists',
    'list_dir',
    'read_bytes',
    'write_bytes',
    'AIOFILES_AVAILABLE',
    # Process
    'run_command',
    'run_shell',
    'run_many',
    'ProcessResult',
    # HTTP
    'HttpClient',
    'HttpResponse',
    'HttpError',
    'get',
    'post',
    'HTTP_CLIENT',
    # Utils
    'run_sync',
    'gather_with_limit',
    'timeout',
    'timeout_or_raise',
    'TimeoutError',
    'retry',
    'retry_async',
    'first_completed',
    'debounce',
    'AsyncLock',
]
