"""
Message Queue System.

SCALE & SUSTAIN Phase 3.3 - Message Queue.

Provides message queue abstractions and implementations:
- Abstract interface for message queues
- In-memory implementation for development
- Redis implementation for production

Author: JuanCS Dev
Date: 2025-11-26
"""

from .interface import (
    IMessageQueue,
    IMessageBroker,
    Message,
    MessageStatus,
    QueueConfig,
)

from .memory import (
    InMemoryQueue,
    InMemoryBroker,
)

from .redis import (
    RedisQueue,
    RedisBroker,
    RedisConfig,
    REDIS_AVAILABLE,
)

from .events import (
    Event,
    EventBus,
    EventHandler,
    event_handler,
)

__all__ = [
    # Interface
    'IMessageQueue',
    'IMessageBroker',
    'Message',
    'MessageStatus',
    'QueueConfig',
    # Memory
    'InMemoryQueue',
    'InMemoryBroker',
    # Redis
    'RedisQueue',
    'RedisBroker',
    'RedisConfig',
    'REDIS_AVAILABLE',
    # Events
    'Event',
    'EventBus',
    'EventHandler',
    'event_handler',
]
