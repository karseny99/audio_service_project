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
    offset: int
    acked_chunk_count: int
    timestamp: datetime

@dataclass
class BitrateChangedEvent(SessionEvent):
    session_id: str
    new_bitrate: int
    timestamp: datetime
