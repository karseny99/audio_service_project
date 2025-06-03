from datetime import datetime
from src.core.logger import logger
from src.core.exceptions import InvalidUseOfControlUseCase

from src.domain.events.publisher import EventPublisher
from src.domain.events.events import (
    BitrateChangedEvent, 
    SessionPaused,
    SessionResumed,
    SessionStopped,
    OffsetChangedEvent,
    SessionHistory
)
from src.domain.stream.models import StreamSession, StreamStatus
from src.domain.stream.repository import StreamingRepository, AudioStreamer


class PauseSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher
        self._session_repo = session_repo

    async def execute(self, session: StreamSession) -> None:
        
        if session.status == StreamStatus.STARTED:
            session.pause()
            logger.info(f"Session {session.session_id} paused")
        else:
            raise InvalidUseOfControlUseCase(f"You can't pause non-started session: Current status is {session.status}")

        await self._session_repo.save(session)

        await self._event_publisher.publish(
            event=SessionPaused(
                session_id=session.session_id,
                timestamp=session.started_at,
            ),
            key=str(session.session_id)
        )
    
    
class ResumeSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher
        self._session_repo = session_repo

    async def execute(self, session: StreamSession) -> None:
        if session.status == StreamStatus.PAUSED:
            session.resume()
            logger.info(f"Session {session.session_id} resumed")
        else:
            raise InvalidUseOfControlUseCase(f"You can't resume non-paused session: Current status is {session.status}")

        await self._session_repo.save(session)

        await self._event_publisher.publish(
            event=SessionResumed(
                session_id=session.session_id,
                timestamp=datetime.now(),
            ),
            key=str(session.session_id)
        )


class StopSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        event_publisher: EventPublisher,
        history_event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher
        self._history_event_publisher = history_event_publisher
        self._session_repo = session_repo

    async def execute(self, session: StreamSession) -> None:
        session.cleanup()
        await self._session_repo.delete(session.session_id)

        await self._event_publisher.publish(
            event=SessionStopped(
                session_id=session.session_id,
                total_chunks_sent=session.total_chunks_sent,
                timestamp=datetime.now(),
            ),
            key=str(session.session_id)
        )

        await self._history_event_publisher.publish(
            event=SessionHistory(
                user_id=session.user_id,
                total_chunks=session.track.total_chunks,
                total_chunks_sent=session.total_chunks_sent,
                timestamp=datetime.now()
            ),
            key=str(session.user_id)
        )


class ChangeSessionBitrateUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        audio_streamer: AudioStreamer,
        event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher
        self._session_repo = session_repo
        self._audio_streamer = audio_streamer

    async def execute(self, new_bitrate: str, session: StreamSession) -> None:
        
        session.switch_bitrate(new_bitrate)
        await self._audio_streamer.switch_bitrate(session.current_bitrate)
        session.track.total_chunks = self._audio_streamer.total_chunks
        
        await self._session_repo.save(session)

        await self._event_publisher.publish(
            event=BitrateChangedEvent(
                session_id=session.session_id,
                new_bitrate=int(session.current_bitrate),
                timestamp=datetime.now(),
            ),
            key=str(session.session_id)
        )

class ChangeSessionOffsetUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        audio_streamer: AudioStreamer,
        event_publisher: EventPublisher,
    ):
        self._event_publisher = event_publisher
        self._session_repo = session_repo
        self._audio_streamer = audio_streamer

    async def execute(self, new_chunk_offset: int, session: StreamSession) -> None:
        old_chunk_offset = session.current_chunk
        session.current_chunk = new_chunk_offset       
        await self._session_repo.save(session)

        await self._event_publisher.publish(
            event=OffsetChangedEvent(
                session_id=session.session_id,
                new_chunk_offset=session.current_chunk,
                old_chunk_offset=old_chunk_offset,
                timestamp=datetime.now(),
            ),
            key=str(session.session_id)
        )
