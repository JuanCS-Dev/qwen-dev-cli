"""
Message Queue Interface.

SCALE & SUSTAIN Phase 3.3 - Message Queue.

Abstract interface for message queue implementations.

Author: JuanCS Dev
Date: 2025-11-26
"""

import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class MessageStatus(Enum):
    """Message processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Message:
    """Message in the queue."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    payload: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    created_at: float = field(default_factory=time.time)
    processed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None

    @property
    def age_seconds(self) -> float:
        """Get message age in seconds."""
        return time.time() - self.created_at

    def mark_processing(self) -> None:
        """Mark message as processing."""
        self.status = MessageStatus.PROCESSING

    def mark_completed(self) -> None:
        """Mark message as completed."""
        self.status = MessageStatus.COMPLETED
        self.processed_at = time.time()

    def mark_failed(self, error: str) -> None:
        """Mark message as failed."""
        self.error = error
        self.retry_count += 1
        if self.retry_count >= self.max_retries:
            self.status = MessageStatus.DEAD_LETTER
        else:
            self.status = MessageStatus.FAILED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'topic': self.topic,
            'payload': self.payload,
            'headers': self.headers,
            'status': self.status.value,
            'created_at': self.created_at,
            'processed_at': self.processed_at,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error': self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary."""
        msg = cls(
            id=data.get('id', str(uuid.uuid4())),
            topic=data.get('topic', ''),
            payload=data.get('payload'),
            headers=data.get('headers', {}),
            created_at=data.get('created_at', time.time()),
            processed_at=data.get('processed_at'),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            error=data.get('error'),
        )
        if 'status' in data:
            msg.status = MessageStatus(data['status'])
        return msg


@dataclass
class QueueConfig:
    """Queue configuration."""

    name: str
    max_size: int = 10000
    max_retries: int = 3
    retry_delay: float = 5.0
    visibility_timeout: float = 30.0
    dead_letter_queue: Optional[str] = None


class IMessageQueue(ABC):
    """
    Abstract message queue interface.

    Implementations must provide:
    - publish: Add message to queue
    - consume: Get next message
    - ack: Acknowledge message processing
    - nack: Negative acknowledge (retry or dead letter)
    """

    @abstractmethod
    async def publish(
        self,
        message: Message,
        delay: float = 0.0
    ) -> str:
        """
        Publish a message to the queue.

        Args:
            message: Message to publish
            delay: Optional delay before message becomes visible

        Returns:
            Message ID
        """
        pass

    @abstractmethod
    async def consume(
        self,
        count: int = 1,
        timeout: float = 0.0
    ) -> List[Message]:
        """
        Consume messages from the queue.

        Args:
            count: Maximum number of messages to consume
            timeout: Wait timeout for messages (0 = no wait)

        Returns:
            List of messages
        """
        pass

    @abstractmethod
    async def ack(self, message_id: str) -> bool:
        """
        Acknowledge message processing.

        Args:
            message_id: ID of message to acknowledge

        Returns:
            True if acknowledged successfully
        """
        pass

    @abstractmethod
    async def nack(
        self,
        message_id: str,
        requeue: bool = True
    ) -> bool:
        """
        Negative acknowledge message.

        Args:
            message_id: ID of message
            requeue: Whether to requeue the message

        Returns:
            True if processed successfully
        """
        pass

    @abstractmethod
    async def size(self) -> int:
        """Get current queue size."""
        pass

    @abstractmethod
    async def purge(self) -> int:
        """Purge all messages from queue. Returns count purged."""
        pass


class IMessageBroker(ABC):
    """
    Abstract message broker interface.

    Manages multiple queues and provides pub/sub functionality.
    """

    @abstractmethod
    async def create_queue(self, config: QueueConfig) -> IMessageQueue:
        """
        Create or get a queue.

        Args:
            config: Queue configuration

        Returns:
            Message queue instance
        """
        pass

    @abstractmethod
    async def delete_queue(self, name: str) -> bool:
        """
        Delete a queue.

        Args:
            name: Queue name

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def get_queue(self, name: str) -> Optional[IMessageQueue]:
        """
        Get an existing queue.

        Args:
            name: Queue name

        Returns:
            Queue instance or None if not found
        """
        pass

    @abstractmethod
    async def list_queues(self) -> List[str]:
        """List all queue names."""
        pass

    @abstractmethod
    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Message], Any],
        queue_name: Optional[str] = None
    ) -> str:
        """
        Subscribe to a topic.

        Args:
            topic: Topic pattern (supports wildcards)
            handler: Message handler function
            queue_name: Optional queue name for persistence

        Returns:
            Subscription ID
        """
        pass

    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from a topic.

        Args:
            subscription_id: Subscription ID

        Returns:
            True if unsubscribed successfully
        """
        pass

    @abstractmethod
    async def publish(
        self,
        topic: str,
        payload: Any,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publish to a topic.

        Args:
            topic: Topic name
            payload: Message payload
            headers: Optional message headers

        Returns:
            Message ID
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the broker and release resources."""
        pass


__all__ = [
    'IMessageQueue',
    'IMessageBroker',
    'Message',
    'MessageStatus',
    'QueueConfig',
]
