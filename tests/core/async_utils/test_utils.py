"""
Tests for async utilities.

SCALE & SUSTAIN Phase 3.1 validation.
"""

import asyncio
import pytest

from jdev_core.async_utils import (
    run_sync,
    gather_with_limit,
    timeout,
    timeout_or_raise,
    TimeoutError,
    retry,
    retry_async,
    first_completed,
    AsyncLock,
)


class TestRunSync:
    """Test run_sync function."""

    def test_run_sync_simple_coroutine(self):
        """Test running a simple coroutine synchronously."""
        async def simple_coro():
            return 42

        result = run_sync(simple_coro())
        assert result == 42

    def test_run_sync_with_await(self):
        """Test run_sync with coroutine that awaits."""
        async def awaiting_coro():
            await asyncio.sleep(0.01)
            return "done"

        result = run_sync(awaiting_coro())
        assert result == "done"


class TestGatherWithLimit:
    """Test gather_with_limit function."""

    @pytest.mark.asyncio
    async def test_gather_with_limit_basic(self):
        """Test basic concurrent execution with limit."""
        async def task(n):
            await asyncio.sleep(0.01)
            return n * 2

        coros = [task(i) for i in range(5)]
        results = await gather_with_limit(coros, limit=2)

        assert results == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_gather_with_limit_preserves_order(self):
        """Test that results are in original order."""
        async def task(n):
            await asyncio.sleep(0.05 - n * 0.01)  # Reverse completion order
            return n

        coros = [task(i) for i in range(3)]
        results = await gather_with_limit(coros, limit=3)

        assert results == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_gather_with_limit_handles_exceptions(self):
        """Test handling exceptions with return_exceptions."""
        async def failing_task(n):
            if n == 2:
                raise ValueError("Task 2 failed")
            return n

        coros = [failing_task(i) for i in range(4)]
        results = await gather_with_limit(coros, limit=2, return_exceptions=True)

        assert results[0] == 0
        assert results[1] == 1
        assert isinstance(results[2], ValueError)
        assert results[3] == 3


class TestTimeout:
    """Test timeout function."""

    @pytest.mark.asyncio
    async def test_timeout_succeeds(self):
        """Test timeout when operation completes in time."""
        async def fast_task():
            await asyncio.sleep(0.01)
            return "completed"

        result = await timeout(fast_task(), seconds=1.0)
        assert result == "completed"

    @pytest.mark.asyncio
    async def test_timeout_returns_default(self):
        """Test timeout returns default on timeout."""
        async def slow_task():
            await asyncio.sleep(10)
            return "never"

        result = await timeout(slow_task(), seconds=0.05, default="timed_out")
        assert result == "timed_out"

    @pytest.mark.asyncio
    async def test_timeout_returns_none_by_default(self):
        """Test timeout returns None when no default specified."""
        async def slow_task():
            await asyncio.sleep(10)

        result = await timeout(slow_task(), seconds=0.05)
        assert result is None


class TestTimeoutOrRaise:
    """Test timeout_or_raise function."""

    @pytest.mark.asyncio
    async def test_timeout_or_raise_succeeds(self):
        """Test timeout_or_raise when operation succeeds."""
        async def fast_task():
            return "done"

        result = await timeout_or_raise(fast_task(), seconds=1.0)
        assert result == "done"

    @pytest.mark.asyncio
    async def test_timeout_or_raise_raises(self):
        """Test timeout_or_raise raises TimeoutError."""
        async def slow_task():
            await asyncio.sleep(10)

        with pytest.raises(TimeoutError) as exc_info:
            await timeout_or_raise(slow_task(), seconds=0.05, message="Custom message")

        assert "Custom message" in str(exc_info.value)
        assert exc_info.value.seconds == 0.05


class TestRetryDecorator:
    """Test retry decorator."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_first_try(self):
        """Test retry when function succeeds immediately."""
        call_count = 0

        @retry(max_attempts=3)
        async def succeeding_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await succeeding_func()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self):
        """Test retry succeeds after initial failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await flaky_func()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self):
        """Test retry raises after exhausting attempts."""
        @retry(max_attempts=2, delay=0.01)
        async def always_fails():
            raise RuntimeError("Always fails")

        with pytest.raises(RuntimeError):
            await always_fails()


class TestRetryAsync:
    """Test retry_async function."""

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test retry_async with successful operation."""
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First try fails")
            return "done"

        result = await retry_async(operation, max_attempts=3, delay=0.01)

        assert result == "done"
        assert call_count == 2


class TestFirstCompleted:
    """Test first_completed function."""

    @pytest.mark.asyncio
    async def test_first_completed_returns_fastest(self):
        """Test that first completed result is returned."""
        async def slow_task():
            await asyncio.sleep(1)
            return "slow"

        async def fast_task():
            await asyncio.sleep(0.01)
            return "fast"

        result = await first_completed([slow_task(), fast_task()])

        assert result == "fast"

    @pytest.mark.asyncio
    async def test_first_completed_cancels_pending(self):
        """Test that pending tasks are cancelled."""
        cancelled = False

        async def cancellable_task():
            nonlocal cancelled
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled = True
                raise

        async def fast_task():
            return "done"

        await first_completed([cancellable_task(), fast_task()])

        # Give time for cancellation to propagate
        await asyncio.sleep(0.01)
        assert cancelled is True


class TestAsyncLock:
    """Test AsyncLock with timeout support."""

    @pytest.mark.asyncio
    async def test_async_lock_basic(self):
        """Test basic lock acquisition."""
        lock = AsyncLock()
        acquired = False

        async with lock:
            acquired = True

        assert acquired is True

    @pytest.mark.asyncio
    async def test_async_lock_with_timeout(self):
        """Test lock acquisition with timeout."""
        lock = AsyncLock()

        async with await lock.acquire(timeout=1.0):
            pass  # Lock acquired successfully

    @pytest.mark.asyncio
    async def test_async_lock_mutual_exclusion(self):
        """Test that lock provides mutual exclusion."""
        lock = AsyncLock()
        results = []

        async def task(name):
            async with lock:
                results.append(f"{name}_start")
                await asyncio.sleep(0.01)
                results.append(f"{name}_end")

        await asyncio.gather(task("A"), task("B"))

        # Check that tasks don't interleave
        a_start = results.index("A_start")
        a_end = results.index("A_end")
        b_start = results.index("B_start")
        b_end = results.index("B_end")

        # Either A completes before B starts, or vice versa
        assert (a_end < b_start) or (b_end < a_start)
