from datetime import datetime
from src.core.protos.generated import UserEvents_pb2
from src.core.protos.generated import StreamEvents_pb2
from src.domain.events.events import UserDeleted, TrackListened
from google.protobuf.timestamp_pb2 import Timestamp

class UserEventConverter:
    @staticmethod
    def convert_user_deleted(proto_event: UserEvents_pb2.UserDeleted) -> UserDeleted:
        return UserDeleted(
            user_id=int(proto_event.user_id),
        )

class TrackEventConverter:
    @staticmethod
    def convert_track_listened(proto_event: StreamEvents_pb2.SessionHistory) -> TrackListened:
        return TrackListened(
            user_id=proto_event.user_id,
            track_id=proto_event.track_id,
            total_chunks_sent=int(proto_event.total_chunks_sent),
            total_chunks=int(proto_event.total_chunks),
            timestamp=proto_event.timestamp.ToDatetime(),
        )
