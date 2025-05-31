from dataclasses import dataclass
from datetime import datetime

class SessionEvent:
    pass

@dataclass
class SessionStarted(SessionEvent):
    session_id: str
    user_id: str
    track_id: str
    bitrate: str
    timestamp: datetime

@dataclass
class ChunksAckEvent(SessionEvent):
    session_id: str
    acked_chunk_count: int
    timestamp: datetime

@dataclass
class BitrateChangedEvent(SessionEvent):
    session_id: str
    new_bitrate: int
    timestamp: datetime

@dataclass
class OffsetChangedEvent(SessionEvent):
    session_id: str
    new_chunk_offset: int
    old_chunk_offset: int
    timestamp: datetime

@dataclass
class SessionPaused(SessionEvent):
    session_id: str
    timestamp: datetime

@dataclass
class SessionResumed(SessionEvent):
    session_id: str
    timestamp: datetime


@dataclass
class SessionStopped(SessionEvent):
    session_id: str
    total_chunks_sent: int
    timestamp: datetime