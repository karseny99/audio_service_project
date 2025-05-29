from dataclasses import dataclass
from datetime import datetime

@dataclass
class SessionStartedEvent:
    session_id: str
    user_id: str
    track_id: str
    timestamp: datetime

@dataclass
class ChunkDeliveredEvent:
    session_id: str
    offset: int
    chunk_size: int

@dataclass
class BitrateChangedEvent:
    session_id: str
    new_bitrate: int
