import uuid
import asyncio
from typing import Optional
from datetime import datetime

from src.core.logger import logger

from src.domain.events.publisher import EventPublisher
from src.domain.events.events import SessionStarted

from src.domain.stream.models import StreamSession, StreamStatus, AudioTrack
from src.domain.stream.repository import StreamingRepository, AudioStreamer

class GetSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        audio_streamer: AudioStreamer,
        event_publisher: EventPublisher,
    ):
        self._session_repo = session_repo 
        self._audio_streamer = audio_streamer
        self._event_publisher = event_publisher

    async def execute(self, track_id: str, user_id: str, bitrate: str, session_id: Optional[str]) -> StreamSession:
        
        if session_id:
            session = await self._session_repo.get(session_id=session_id)
            await self._audio_streamer.initialize(session.track.track_id, session.current_bitrate)
            self._audio_streamer.seek(session.current_chunk * self._audio_streamer.chunk_size)
            return session
        
        track = AudioTrack(
            track_id=track_id,
            total_chunks=self._audio_streamer.total_chunks,
            available_bitrates= await self._audio_streamer.get_bitrates(),
            duration_ms=self._audio_streamer.duration / 1000, # source value in seconds
        )

        session = StreamSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            track=track,
            current_bitrate=bitrate,
            chunk_size=self._audio_streamer.chunk_size,
            status=StreamStatus.STARTED,
            current_chunk=0,
            started_at=datetime.now(),
            message_queue=asyncio.Queue(),
        )

        await self._event_publisher.publish(
            event=SessionStarted(
                session_id=session.session_id,
                user_id=session.user_id,    
                track_id=session.track.track_id,
                bitrate=session.current_bitrate,
                timestamp=session.started_at,
            ),
            key=str(session.user_id)
        )

        return session