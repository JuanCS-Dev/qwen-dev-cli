"""
Session Manager.

SCALE & SUSTAIN Phase 1.1.3 - Session Manager.

Manages conversation sessions with persistence and context.

Author: JuanCS Dev
Date: 2025-11-26
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


class SessionState(Enum):
    """Session lifecycle state."""
    CREATED = auto()
    ACTIVE = auto()
    PAUSED = auto()
    COMPLETED = auto()
    EXPIRED = auto()
    ERROR = auto()


@dataclass
class SessionConfig:
    """Session configuration."""
    auto_save: bool = True
    save_interval: int = 60  # seconds
    history_limit: int = 100
    context_window: int = 8192
    persist_path: Optional[Path] = None


@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Session:
    """Represents a conversation session."""
    id: str
    created_at: float
    state: SessionState = SessionState.CREATED
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the session."""
        self.messages.append(ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        self.last_activity = time.time()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        messages = self.messages[-limit:] if limit else self.messages
        return [m.to_dict() for m in messages]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "created_at": self.created_at,
            "state": self.state.name,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context,
            "metadata": self.metadata,
            "last_activity": self.last_activity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create from dictionary."""
        session = cls(
            id=data["id"],
            created_at=data["created_at"],
            state=SessionState[data.get("state", "CREATED")],
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
            last_activity=data.get("last_activity", time.time()),
        )
        session.messages = [
            ConversationMessage.from_dict(m) for m in data.get("messages", [])
        ]
        return session


class SessionManager:
    """
    Manages conversation sessions.

    Features:
    - Session creation and lifecycle management
    - Conversation history tracking
    - Context persistence
    - Auto-save functionality
    - Session recovery

    Example:
        manager = SessionManager(config=SessionConfig(auto_save=True))

        # Create new session
        session = manager.create_session()

        # Add messages
        manager.add_message(session.id, "user", "Hello!")
        manager.add_message(session.id, "assistant", "Hi there!")

        # Get history
        history = manager.get_history(session.id, limit=10)

        # Save and restore
        manager.save_session(session.id)
        restored = manager.load_session(session.id)
    """

    def __init__(
        self,
        config: Optional[SessionConfig] = None,
        sessions_dir: Optional[Path] = None
    ):
        self._config = config or SessionConfig()
        self._sessions_dir = sessions_dir or Path.home() / ".jdev" / "sessions"
        self._sessions: Dict[str, Session] = {}
        self._current_session_id: Optional[str] = None
        self._lock = threading.RLock()

        # Ensure sessions directory exists
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Session:
        """Create a new session."""
        with self._lock:
            session = Session(
                id=session_id or str(uuid.uuid4()),
                created_at=time.time(),
                state=SessionState.ACTIVE,
                context=context or {},
                metadata=metadata or {},
            )

            self._sessions[session.id] = session
            self._current_session_id = session.id

            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    def get_current_session(self) -> Optional[Session]:
        """Get the current active session."""
        if self._current_session_id:
            return self._sessions.get(self._current_session_id)
        return None

    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session."""
        if session_id in self._sessions:
            self._current_session_id = session_id
            return True
        return False

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a message to a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.add_message(role, content, metadata)

        # Trim history if needed
        if len(session.messages) > self._config.history_limit:
            session.messages = session.messages[-self._config.history_limit:]

        # Auto-save
        if self._config.auto_save:
            self.save_session(session_id)

        return True

    def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []

        return session.get_history(limit)

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context."""
        session = self._sessions.get(session_id)
        if not session:
            return {}
        return session.context.copy()

    def update_context(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update session context."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.context.update(updates)
        session.last_activity = time.time()

        if self._config.auto_save:
            self.save_session(session_id)

        return True

    def save_session(self, session_id: str) -> bool:
        """Save session to disk."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        try:
            path = self._sessions_dir / f"{session_id}.json"
            with open(path, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            return True
        except IOError:
            return False

    def load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk."""
        path = self._sessions_dir / f"{session_id}.json"

        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)

            session = Session.from_dict(data)
            self._sessions[session.id] = session
            return session

        except (json.JSONDecodeError, IOError, KeyError):
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions (memory + disk)."""
        sessions = []

        # Memory sessions
        for session in self._sessions.values():
            sessions.append({
                "id": session.id,
                "created_at": session.created_at,
                "state": session.state.name,
                "message_count": len(session.messages),
                "last_activity": session.last_activity,
            })

        # Disk sessions not in memory
        for path in self._sessions_dir.glob("*.json"):
            session_id = path.stem
            if session_id not in self._sessions:
                try:
                    with open(path) as f:
                        data = json.load(f)
                    sessions.append({
                        "id": data["id"],
                        "created_at": data["created_at"],
                        "state": data.get("state", "UNKNOWN"),
                        "message_count": len(data.get("messages", [])),
                        "last_activity": data.get("last_activity", 0),
                        "persisted": True,
                    })
                except (json.JSONDecodeError, IOError):
                    pass

        return sorted(sessions, key=lambda s: s.get("last_activity", 0), reverse=True)

    def close_session(self, session_id: str) -> bool:
        """Close and save a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.state = SessionState.COMPLETED
        self.save_session(session_id)

        if self._current_session_id == session_id:
            self._current_session_id = None

        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session completely."""
        # Remove from memory
        if session_id in self._sessions:
            del self._sessions[session_id]

        # Remove from disk
        path = self._sessions_dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True

        return session_id in self._sessions

    def cleanup_expired(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions."""
        cutoff = time.time() - (max_age_hours * 3600)
        cleaned = 0

        with self._lock:
            # Memory sessions
            expired = [
                sid for sid, s in self._sessions.items()
                if s.last_activity < cutoff
            ]
            for sid in expired:
                self.close_session(sid)
                cleaned += 1

            # Disk sessions
            for path in self._sessions_dir.glob("*.json"):
                try:
                    stat = path.stat()
                    if stat.st_mtime < cutoff:
                        path.unlink()
                        cleaned += 1
                except IOError:
                    pass

        return cleaned

    @property
    def active_session_count(self) -> int:
        """Get count of active sessions."""
        return sum(
            1 for s in self._sessions.values()
            if s.state == SessionState.ACTIVE
        )


__all__ = ['SessionManager', 'SessionState', 'SessionConfig', 'Session', 'ConversationMessage']
