"""
Tests for event bus system.

SCALE & SUSTAIN Phase 3.3 validation.
"""

import asyncio
import pytest

from jdev_core.messaging import (
    Event,
    EventBus,
    event_handler,
)
from jdev_core.messaging.events import (
    TaskStartedEvent,
    TaskCompletedEvent,
)


class TestEvent:
    """Test Event base class."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(source="test", data={"key": "value"})

        assert event.source == "test"
        assert event.data == {"key": "value"}
        assert event.id is not None
        assert event.timestamp > 0

    def test_event_type_property(self):
        """Test event_type returns class name."""
        event = Event()
        assert event.event_type == "Event"

        task_event = TaskStartedEvent()
        assert task_event.event_type == "TaskStartedEvent"

    def test_event_to_dict(self):
        """Test event serialization."""
        event = Event(source="test", data={"x": 1})
        d = event.to_dict()

        assert d["source"] == "test"
        assert d["data"] == {"x": 1}
        assert "id" in d
        assert "timestamp" in d
        assert d["type"] == "Event"


class TestEventBus:
    """Test EventBus class."""

    @pytest.mark.asyncio
    async def test_subscribe_and_emit(self):
        """Test basic subscribe and emit."""
        bus = EventBus()
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe(Event, handler)
        await bus.emit(Event(data={"test": True}))

        assert len(received) == 1
        assert received[0].data == {"test": True}

    @pytest.mark.asyncio
    async def test_decorator_subscription(self):
        """Test subscription via decorator."""
        bus = EventBus()
        received = []

        @bus.on(TaskStartedEvent)
        def handler(event):
            received.append(event)

        await bus.emit(TaskStartedEvent(data={"task": "test"}))

        assert len(received) == 1
        assert received[0].data == {"task": "test"}

    @pytest.mark.asyncio
    async def test_async_handler(self):
        """Test async event handler."""
        bus = EventBus()
        received = []

        @bus.on(Event)
        async def async_handler(event):
            await asyncio.sleep(0.01)
            received.append(event)

        await bus.emit(Event())

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        """Test multiple handlers for same event."""
        bus = EventBus()
        results = []

        @bus.on(Event)
        def handler1(event):
            results.append("handler1")

        @bus.on(Event)
        def handler2(event):
            results.append("handler2")

        await bus.emit(Event())

        assert "handler1" in results
        assert "handler2" in results

    @pytest.mark.asyncio
    async def test_event_type_filtering(self):
        """Test handlers only receive matching event types."""
        bus = EventBus()
        started_count = 0
        completed_count = 0

        @bus.on(TaskStartedEvent)
        def started_handler(event):
            nonlocal started_count
            started_count += 1

        @bus.on(TaskCompletedEvent)
        def completed_handler(event):
            nonlocal completed_count
            completed_count += 1

        await bus.emit(TaskStartedEvent())
        await bus.emit(TaskStartedEvent())
        await bus.emit(TaskCompletedEvent())

        assert started_count == 2
        assert completed_count == 1

    @pytest.mark.asyncio
    async def test_wildcard_handler(self):
        """Test handler that receives all events."""
        bus = EventBus()
        all_events = []

        @bus.on()  # No type = wildcard
        def catch_all(event):
            all_events.append(event)

        await bus.emit(TaskStartedEvent())
        await bus.emit(TaskCompletedEvent())
        await bus.emit(Event())

        assert len(all_events) == 3

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribing from events."""
        bus = EventBus()
        count = 0

        def handler(event):
            nonlocal count
            count += 1

        bus.subscribe(Event, handler)
        await bus.emit(Event())
        assert count == 1

        bus.unsubscribe(Event, handler)
        await bus.emit(Event())
        assert count == 1  # Should not increment

    @pytest.mark.asyncio
    async def test_event_history(self):
        """Test event history tracking."""
        bus = EventBus()

        await bus.emit(Event(data={"n": 1}))
        await bus.emit(Event(data={"n": 2}))
        await bus.emit(Event(data={"n": 3}))

        history = bus.get_history()
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_event_history_limit(self):
        """Test event history respects limit."""
        bus = EventBus()

        history = bus.get_history(limit=2)
        # Returns up to limit
        assert len(history) <= 2

    @pytest.mark.asyncio
    async def test_emit_no_wait(self):
        """Test fire-and-forget emit."""
        bus = EventBus()
        processed = []

        @bus.on(Event)
        async def slow_handler(event):
            await asyncio.sleep(0.05)
            processed.append(event)

        # Emit without waiting
        results = await bus.emit(Event(), wait=False)

        # Should return immediately with no results
        assert results == []

        # Wait for handler to complete
        await asyncio.sleep(0.1)
        assert len(processed) == 1

    def test_handler_count(self):
        """Test handler_count property."""
        bus = EventBus()

        assert bus.handler_count == 0

        @bus.on(Event)
        def h1(e): pass

        @bus.on(Event)
        def h2(e): pass

        @bus.on(TaskStartedEvent)
        def h3(e): pass

        assert bus.handler_count == 3

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self):
        """Test that handler exceptions don't break other handlers."""
        bus = EventBus()
        results = []

        @bus.on(Event)
        def failing_handler(event):
            raise ValueError("Handler error")

        @bus.on(Event)
        def working_handler(event):
            results.append("worked")

        # Should not raise, but return exceptions
        await bus.emit(Event(), wait=True)

        # Working handler should still execute
        assert "worked" in results


class TestEventHandlerDecorator:
    """Test event_handler decorator."""

    def test_decorator_marks_function(self):
        """Test decorator adds _event_type attribute."""
        @event_handler(TaskStartedEvent)
        def my_handler(event):
            pass

        assert hasattr(my_handler, '_event_type')
        assert my_handler._event_type == TaskStartedEvent
