from datetime import datetime
from dataclasses import dataclass
from google.protobuf.message import Message


class HistoryEvent:
    pass

@dataclass
class UserDeleted:
    user_id: int

@dataclass
class UserLikedTrackEvent(HistoryEvent):
    user_id: int
    track_id: int
    timestamp: datetime

@dataclass 
class TrackListened:
    current_chunk: int
    total_chunks: int