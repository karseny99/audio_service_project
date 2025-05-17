from src.core.protos.generated import UserEvents_pb2
from src.domain.events.events import UserDeleted
from src.domain.playlists.value_objects import UserId

class UserEventConverter:
    @staticmethod
    def convert_user_deleted(proto_event: UserEvents_pb2.UserDeleted) -> UserDeleted:
        return UserDeleted(
            user_id=int(proto_event.user_id),
        )
