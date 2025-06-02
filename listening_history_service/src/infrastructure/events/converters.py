from src.core.protos.generated import UserEvents_pb2
from src.core.protos.generated import TrackEvents_pb2
from src.domain.events.events import UserDeleted, TrackListened

class UserEventConverter:
    @staticmethod
    def convert_user_deleted(proto_event: UserEvents_pb2.UserDeleted) -> UserDeleted:
        return UserDeleted(
            user_id=int(proto_event.user_id),
        )

class TrackEventConverter:
    @staticmethod
    def convert_track_listened(proto_event: TrackEvents_pb2.TrackListened) -> TrackListened:
        return TrackListened(
            current_chunk=int(proto_event.current_chunk),
            total_chunks=int(proto_event.total_chunks),
        )
