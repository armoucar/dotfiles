"""Data models for tmux state management."""

import dataclasses as dc
import json
from typing import List, Optional


@dc.dataclass
class Window:
    """Represents a tmux window."""

    index: int
    name: str
    path: str
    ordinal: int  # nth occurrence of (name, path) within the session


@dc.dataclass
class Session:
    """Represents a tmux session."""

    name: str
    windows: List[Window]


@dc.dataclass
class ClaudeBinding:
    """Represents a binding between a tmux window and a Claude session."""

    session: str
    window_name: str
    path: str
    ordinal: int
    uuid: str


@dc.dataclass
class State:
    """Complete tmux state snapshot."""

    created_at: str
    sessions: List[Session]
    current_session: Optional[str]
    current_window_index: Optional[int]
    claude: List[ClaudeBinding]

    def to_json(self) -> str:
        """Convert state to JSON string."""
        return json.dumps(dc.asdict(self), indent=2)

    @staticmethod
    def from_json(data: str) -> "State":
        """Create State from JSON string."""
        obj = json.loads(data)
        sessions = []
        for s in obj.get("sessions", []):
            windows = [Window(**w) for w in s.get("windows", [])]
            sessions.append(Session(name=s["name"], windows=windows))
        claude = [ClaudeBinding(**c) for c in obj.get("claude", [])]
        return State(
            created_at=obj.get("created_at"),
            sessions=sessions,
            current_session=obj.get("current_session"),
            current_window_index=obj.get("current_window_index"),
            claude=claude,
        )
