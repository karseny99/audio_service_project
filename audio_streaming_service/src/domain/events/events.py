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
class ChunkDeliveredEvent(SessionEvent):
    session_id: str
    offset: int
    chunk_size: int

@dataclass
class BitrateChangedEvent(SessionEvent):
    session_id: str
    new_bitrate: int
