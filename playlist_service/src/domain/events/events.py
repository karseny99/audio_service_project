from datetime import datetime
from dataclasses import dataclass
from google.protobuf.message import Message
from src.domain.playlists.value_objects import UserId


class PlaylistEvent:
    """
        Base class for playlist events
    """
    pass

@dataclass
class TrackAddedToPlaylist(PlaylistEvent):
    playlist_id: int
    track_id: int
    user_id: int
    timestamp: datetime