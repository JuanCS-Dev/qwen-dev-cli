"""
In-Memory Message Queue.

SCALE & SUSTAIN Phase 3.3 - Message Queue.

In-memory implementation for development and testing.

Author: JuanCS Dev
Date: 2025-11-26
"""

import asyncio
import fnmatch
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from .interface import (
    IMessageQueue,
    IMessageBroker,
    Message,
    MessageStatus,
    QueueConfig,
)


class InMemoryQueue(IMessageQueue):
    """
    In-memory message queue implementation.

    Suitable for development, testing, and single-process applications.
    """

    def __init__(self, config: QueueConfig):
        self._config = config
        self._messages: asyncio.Queue[Message] = asyncio.Queue(maxsize=config.max_size)
        self._processing: Dict[str, Message] = {}
        self._delayed: List[tuple[float, Message]] = []
        self._lock = asyncio.Lock()

    async def publish(
        self,
        message: Message,
        delay: float = 0.0
    ) -> str:
        """Publish a message to the queue."""
        message.max_retries = self._config.max_retries

        if delay > 0:
            async with self._lock:
                visible_at = time.time() + delay
                self._delayed.append((visible_at, message))
                self._delayed.sort(key=lambda x: x[0])
            return message.id

        try:
            self._messages.put_nowait(message)
            return message.id
        except asyncio.QueueFull:
            raise Exception(f"Queue {self._config.name} is full")

    async def consume(
        self,
        count: int = 1,
        timeout: float = 0.0
    ) -> List[Message]:
        """Consume messages from the queue."""
        # First, move any delayed messages that are now visible
        await self._process_delayed()

        messages = []
        deadline = time.time() + timeout if timeout > 0 else 0

        for _ in range(count):
            try:
                if timeout > 0:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        break
                    message = await asyncio.wait_for(
                        self._messages.get(),
                        timeout=remaining
                    )
                else:
                    message = self._messages.get_nowait()

                message.mark_processing()
                async with self._lock:
                    self._processing[message.id] = message
                messages.append(message)

            except (asyncio.QueueEmpty, asyncio.TimeoutError):
                break

        return messages

    async def _process_delayed(self) -> None:
        """Move delayed messages to main queue if visible."""
        async with self._lock:
            now = time.time()
            while self._delayed and self._delayed[0][0] <= now:
                _, message = self._delayed.pop(0)
                try:
                    self._messages.put_nowait(message)
                except asyncio.QueueFull:
                    # Put back in delayed queue
                    self._delayed.insert(0, (now, message))
                    break

    async def ack(self, message_id: str) -> bool:
        """Acknowledge message processing."""
        async with self._lock:
            if message_id in self._processing:
                message = self._processing.pop(message_id)
                message.mark_completed()
                return True
            return False

    async def nack(
        self,
        message_id: str,
        requeue: bool = True
    ) -> bool:
        """Negative acknowledge message."""
        async with self._lock:
            if message_id not in self._processing:
                return False

            message = self._processing.pop(message_id)
            message.mark_failed("Negative acknowledgement")

            if requeue and message.status != MessageStatus.DEAD_LETTER:
                # Requeue with delay
                visible_at = time.time() + self._config.retry_delay
                self._delayed.append((visible_at, message))
                self._delayed.sort(key=lambda x: x[0])
            elif self._config.dead_letter_queue:
                # Would send to dead letter queue in production
                pass

            return True

    async def size(self) -> int:
        """Get current queue size."""
        return self._messages.qsize() + len(self._delayed)

    async def purge(self) -> int:
        """Purge all messages."""
        async with self._lock:
            count = self._messages.qsize() + len(self._delayed)

            # Clear main queue
            while not self._messages.empty():
                try:
                    self._messages.get_nowait()
                except asyncio.QueueEmpty:
                    break

            # Clear delayed
            self._delayed.clear()

            return count


class InMemoryBroker(IMessageBroker):
    """
    In-memory message broker implementation.

    Provides queue management and pub/sub functionality.
    """

    def __init__(self):
        self._queues: Dict[str, InMemoryQueue] = {}
        self._subscriptions: Dict[str, tuple[str, Callable, Optional[str]]] = {}
        self._running = False
        self._dispatch_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def create_queue(self, config: QueueConfig) -> IMessageQueue:
        """Create or get a queue."""
        async with self._lock:
            if config.name not in self._queues:
                self._queues[config.name] = InMemoryQueue(config)
            return self._queues[config.name]

    async def delete_queue(self, name: str) -> bool:
        """Delete a queue."""
        async with self._lock:
            if name in self._queues:
                await self._queues[name].purge()
                del self._queues[name]
                return True
            return False

    async def get_queue(self, name: str) -> Optional[IMessageQueue]:
        """Get an existing queue."""
        return self._queues.get(name)

    async def list_queues(self) -> List[str]:
        """List all queue names."""
        return list(self._queues.keys())

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], Any],
        queue_name: Optional[str] = None
    ) -> str:
        """Subscribe to a topic."""
        subscription_id = str(uuid.uuid4())

        async with self._lock:
            self._subscriptions[subscription_id] = (topic, handler, queue_name)

            # Create queue if specified
            if queue_name and queue_name not in self._queues:
                await self.create_queue(QueueConfig(name=queue_name))

        # Start dispatcher if not running
        if not self._running:
            await self._start_dispatcher()

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        async with self._lock:
            if subscription_id in self._subscriptions:
                del self._subscriptions[subscription_id]
                return True
            return False

    async def publish(
        self,
        topic: str,
        payload: Any,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Publish to a topic."""
        message = Message(
            topic=topic,
            payload=payload,
            headers=headers or {}
        )

        # Dispatch to matching subscribers
        async with self._lock:
            for sub_id, (pattern, handler, queue_name) in self._subscriptions.items():
                if self._matches_topic(topic, pattern):
                    if queue_name:
                        # Queue for later processing
                        queue = self._queues.get(queue_name)
                        if queue:
                            await queue.publish(message)
                    else:
                        # Direct dispatch
                        asyncio.create_task(self._invoke_handler(handler, message))

        return message.id

    def _matches_topic(self, topic: str, pattern: str) -> bool:
        """Check if topic matches subscription pattern."""
        # Support wildcards: * matches one segment, # matches all remaining
        if pattern == topic:
            return True

        # Convert MQTT-style wildcards to fnmatch patterns
        fnmatch_pattern = pattern.replace('+', '*').replace('#', '**')
        return fnmatch.fnmatch(topic, fnmatch_pattern)

    async def _invoke_handler(
        self,
        handler: Callable[[Message], Any],
        message: Message
    ) -> None:
        """Invoke a message handler safely."""
        try:
            result = handler(message)
            if asyncio.iscoroutine(result):
                await result
        except Exception:
            # Log error in production
            pass

    async def _start_dispatcher(self) -> None:
        """Start the message dispatcher."""
        if self._running:
            return

        self._running = True
        self._dispatch_task = asyncio.create_task(self._dispatch_loop())

    async def _dispatch_loop(self) -> None:
        """Continuous message dispatch loop."""
        while self._running:
            # Process messages from subscriber queues
            async with self._lock:
                for sub_id, (pattern, handler, queue_name) in list(self._subscriptions.items()):
                    if queue_name and queue_name in self._queues:
                        queue = self._queues[queue_name]
                        messages = await queue.consume(count=10, timeout=0)
                        for message in messages:
                            try:
                                await self._invoke_handler(handler, message)
                                await queue.ack(message.id)
                            except Exception:
                                await queue.nack(message.id)

            await asyncio.sleep(0.1)  # Small delay between dispatch cycles

    async def close(self) -> None:
        """Close the broker."""
        self._running = False

        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass

        # Purge all queues
        for queue in self._queues.values():
            await queue.purge()

        self._queues.clear()
        self._subscriptions.clear()


# Global broker instance
_global_broker: Optional[InMemoryBroker] = None


def get_message_broker() -> InMemoryBroker:
    """Get or create the global message broker."""
    global _global_broker
    if _global_broker is None:
        _global_broker = InMemoryBroker()
    return _global_broker


__all__ = [
    'InMemoryQueue',
    'InMemoryBroker',
    'get_message_broker',
]
