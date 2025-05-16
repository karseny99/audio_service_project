from dataclasses import dataclass
from google.protobuf.message import Message
from src.domain.playlists.value_objects import UserId


class PlaylistEvent:
    """
        Base class for playlist events
    """
    def to_proto(self) -> Message:
        raise NotImplementedError

    def get_headers(self) -> dict:
        return {'event-type': self.__class__.__name__}


@dataclass
class UserDeleted:
    user_id: int