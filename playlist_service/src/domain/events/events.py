from dataclasses import dataclass
from google.protobuf.message import Message
from src.domain.playlists.value_objects import UserId


class PlaylistEvent:
    """
        Base class for playlist events
    """
    pass

@dataclass
class UserDeleted:
    user_id: int