from functools import singledispatchmethod
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from src.core.config import settings
from src.infrastructure.events.base_converter import BaseEventConverter

from src.core.protos.generated.events_pb2 import (
    SessionStarted as SessionStartedProto,
    ChunksAckEvent as ChunksAckEventProto,
    BitrateChangedEvent as BitrateChangedEventProto,
    OffsetChangedEvent as OffsetChangedEventProto,
    SessionPaused as SessionPausedProto,
    SessionResumed as SessionResumedProto,
    SessionStopped as SessionStoppedProto,
    SessionHistory as SessionHistoryProto,
)

from src.domain.events.events import (
    SessionStarted,
    ChunksAckEvent,
    BitrateChangedEvent,
    OffsetChangedEvent,
    SessionPaused,
    SessionResumed,
    SessionStopped,
    SessionHistory,
)

class SessionEventConverters(BaseEventConverter):
    @staticmethod
    def _convert_datetime_to_proto(dt: datetime) -> Timestamp:
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

    @singledispatchmethod
    @staticmethod
    def to_proto(event):
        raise NotImplementedError(f"No proto converter for {type(event).__name__}")

    @to_proto.register
    @staticmethod
    def _(event: SessionStarted) -> SessionStartedProto:
        return SessionStartedProto(
            session_id=event.session_id,
            user_id=event.user_id,
            track_id=event.track_id,
            bitrate=event.bitrate,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: ChunksAckEvent) -> ChunksAckEventProto:
        return ChunksAckEventProto(
            session_id=event.session_id,
            acked_chunk_count=event.acked_chunk_count,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: BitrateChangedEvent) -> BitrateChangedEventProto:
        return BitrateChangedEventProto(
            session_id=event.session_id,
            new_bitrate=event.new_bitrate,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: OffsetChangedEvent) -> OffsetChangedEventProto:
        return OffsetChangedEventProto(
            session_id=event.session_id,
            new_chunk_offset=event.new_chunk_offset,
            old_chunk_offset=event.old_chunk_offset,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: SessionPaused) -> SessionPausedProto:
        return SessionPausedProto(
            session_id=event.session_id,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: SessionResumed) -> SessionResumedProto:
        return SessionResumedProto(
            session_id=event.session_id,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: SessionStopped) -> SessionStoppedProto:
        return SessionStoppedProto(
            session_id=event.session_id,
            total_chunks_sent=event.total_chunks_sent,
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @to_proto.register
    @staticmethod
    def _(event: SessionHistory) -> SessionHistoryProto:
        return SessionHistoryProto(
            user_id=int(event.user_id),
            track_id=int(event.track_id),
            total_chunks_sent=int(event.total_chunks_sent),
            total_chunks=int(event.total_chunks),
            timestamp=SessionEventConverters._convert_datetime_to_proto(event.timestamp)
        )

    @staticmethod
    def get_headers(event) -> dict:
        return {settings.EVENT_HEADER: event.__class__.__name__}
