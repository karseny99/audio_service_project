import uuid
import asyncio
from typing import Optional
from datetime import datetime

from src.core.logger import logger

from src.domain.events.publisher import EventPublisher
from src.domain.events.events import SessionStarted

from src.domain.stream.models import StreamSession, StreamStatus, AudioTrack
from src.domain.stream.repository import StreamingRepository, AudioStreamer

class UpdateSessionUseCase:
    def __init__(
        self,
        session_repo: StreamingRepository,
        audio_streamer: AudioStreamer,
    ):
        self._session_repo = session_repo 
        self._audio_streamer = audio_streamer

    async def execute(self, session: StreamSession) -> None:
        await self._session_repo.save(session)

