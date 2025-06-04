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
class TrackListened(HistoryEvent):
    user_id: int
    track_id: int
    total_chunks_sent: int
    total_chunks: int
    timestamp: datetime