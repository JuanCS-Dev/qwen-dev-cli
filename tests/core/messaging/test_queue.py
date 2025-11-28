"""
Tests for message queue.

SCALE & SUSTAIN Phase 3.3 validation.
"""

import asyncio
import pytest

from jdev_core.messaging import (
    Message,
    MessageStatus,
    QueueConfig,
    InMemoryQueue,
    InMemoryBroker,
)


class TestMessage:
    """Test Message dataclass."""

    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message(topic="test.topic", payload={"data": 123})

        assert msg.topic == "test.topic"
        assert msg.payload == {"data": 123}
        assert msg.status == MessageStatus.PENDING
        assert msg.id is not None

    def test_message_mark_processing(self):
        """Test marking message as processing."""
        msg = Message()
        msg.mark_processing()

        assert msg.status == MessageStatus.PROCESSING

    def test_message_mark_completed(self):
        """Test marking message as completed."""
        msg = Message()
        msg.mark_completed()

        assert msg.status == MessageStatus.COMPLETED
        assert msg.processed_at is not None

    def test_message_mark_failed(self):
        """Test marking message as failed."""
        msg = Message(max_retries=3)
        msg.mark_failed("Error occurred")

        assert msg.status == MessageStatus.FAILED
        assert msg.error == "Error occurred"
        assert msg.retry_count == 1

    def test_message_dead_letter_after_max_retries(self):
        """Test message goes to dead letter after max retries."""
        msg = Message(max_retries=2)

        msg.mark_failed("Error 1")
        assert msg.status == MessageStatus.FAILED

        msg.mark_failed("Error 2")
        assert msg.status == MessageStatus.DEAD_LETTER

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = Message(topic="test", payload="data")
        d = msg.to_dict()

        assert d["topic"] == "test"
        assert d["payload"] == "data"
        assert "id" in d

    def test_message_from_dict(self):
        """Test message deserialization."""
        data = {
            "id": "test-id",
            "topic": "test.topic",
            "payload": {"key": "value"},
            "status": "completed",
        }
        msg = Message.from_dict(data)

        assert msg.id == "test-id"
        assert msg.topic == "test.topic"
        assert msg.status == MessageStatus.COMPLETED


class TestInMemoryQueue:
    """Test InMemoryQueue class."""

    @pytest.fixture
    def queue(self):
        """Create a test queue."""
        config = QueueConfig(name="test-queue", max_size=100)
        return InMemoryQueue(config)

    @pytest.mark.asyncio
    async def test_publish_and_consume(self, queue):
        """Test basic publish and consume."""
        msg = Message(payload="test data")
        await queue.publish(msg)

        messages = await queue.consume(count=1)

        assert len(messages) == 1
        assert messages[0].payload == "test data"
        assert messages[0].status == MessageStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_ack_message(self, queue):
        """Test acknowledging a message."""
        msg = Message(payload="ack test")
        await queue.publish(msg)

        messages = await queue.consume(count=1)
        result = await queue.ack(messages[0].id)

        assert result is True

    @pytest.mark.asyncio
    async def test_nack_message(self, queue):
        """Test negative acknowledgment."""
        msg = Message(payload="nack test")
        await queue.publish(msg)

        messages = await queue.consume(count=1)
        result = await queue.nack(messages[0].id, requeue=True)

        assert result is True

    @pytest.mark.asyncio
    async def test_queue_size(self, queue):
        """Test queue size tracking."""
        assert await queue.size() == 0

        await queue.publish(Message(payload="1"))
        await queue.publish(Message(payload="2"))

        assert await queue.size() == 2

        await queue.consume(count=1)
        assert await queue.size() == 1

    @pytest.mark.asyncio
    async def test_queue_purge(self, queue):
        """Test purging all messages."""
        await queue.publish(Message(payload="1"))
        await queue.publish(Message(payload="2"))
        await queue.publish(Message(payload="3"))

        count = await queue.purge()

        assert count == 3
        assert await queue.size() == 0

    @pytest.mark.asyncio
    async def test_delayed_publish(self, queue):
        """Test delayed message publishing."""
        msg = Message(payload="delayed")
        await queue.publish(msg, delay=0.1)

        # Should not be available immediately
        messages = await queue.consume(count=1, timeout=0)
        assert len(messages) == 0

        # Wait for delay
        await asyncio.sleep(0.15)
        messages = await queue.consume(count=1, timeout=0)
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_consume_with_timeout(self, queue):
        """Test consuming with wait timeout."""
        # Start consuming in background
        async def delayed_publish():
            await asyncio.sleep(0.05)
            await queue.publish(Message(payload="delayed"))

        asyncio.create_task(delayed_publish())

        # Should wait and receive the message
        messages = await queue.consume(count=1, timeout=0.5)
        assert len(messages) == 1


class TestInMemoryBroker:
    """Test InMemoryBroker class."""

    @pytest.fixture
    def broker(self):
        """Create a test broker."""
        return InMemoryBroker()

    @pytest.mark.asyncio
    async def test_create_queue(self, broker):
        """Test creating a queue."""
        config = QueueConfig(name="my-queue")
        queue = await broker.create_queue(config)

        assert queue is not None
        assert "my-queue" in await broker.list_queues()

    @pytest.mark.asyncio
    async def test_get_queue(self, broker):
        """Test getting an existing queue."""
        config = QueueConfig(name="test-queue")
        await broker.create_queue(config)

        queue = await broker.get_queue("test-queue")
        assert queue is not None

        missing = await broker.get_queue("nonexistent")
        assert missing is None

    @pytest.mark.asyncio
    async def test_delete_queue(self, broker):
        """Test deleting a queue."""
        config = QueueConfig(name="to-delete")
        await broker.create_queue(config)

        result = await broker.delete_queue("to-delete")
        assert result is True

        assert "to-delete" not in await broker.list_queues()

    @pytest.mark.asyncio
    async def test_pubsub_direct(self, broker):
        """Test pub/sub with direct dispatch."""
        received = []

        async def handler(msg):
            received.append(msg)

        await broker.subscribe("test.topic", handler)
        await broker.publish("test.topic", {"data": "value"})

        # Wait for dispatch
        await asyncio.sleep(0.05)

        assert len(received) == 1
        assert received[0].payload == {"data": "value"}

    @pytest.mark.asyncio
    async def test_unsubscribe(self, broker):
        """Test unsubscribing from topic."""
        received = []

        def handler(msg):
            received.append(msg)

        sub_id = await broker.subscribe("test.topic", handler)
        await broker.publish("test.topic", "first")
        await asyncio.sleep(0.05)

        await broker.unsubscribe(sub_id)
        await broker.publish("test.topic", "second")
        await asyncio.sleep(0.05)

        assert len(received) == 1  # Only received first message

    @pytest.mark.asyncio
    async def test_broker_close(self, broker):
        """Test closing the broker."""
        config = QueueConfig(name="test")
        await broker.create_queue(config)

        await broker.close()

        assert await broker.list_queues() == []
