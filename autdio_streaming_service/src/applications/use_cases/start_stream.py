from datetime import datetime
import uuid

from domain.stream.models import StreamingSession
from src.domain.events.events import SessionStartedEvent
from src.domain.events.publisher import EventPublisher
from src.domain.tracks.services import AbstractTrackService
from src.domain.stream.repository import StreamingSessionRepository
from src.core.exceptions import TrackNotFoundError

class StartStreamUseCase:
    def __init__(
        self,
        session_repo: StreamingSessionRepository,
        track_service: AbstractTrackService,
        event_publisher: EventPublisher,
    ):
        self._session_repo = session_repo
        self._track_service = track_service
        self._event_publisher = event_publisher

    async def execute(self, user_id: str, track_id: str, bitrate: int) -> str:
        # Получаем метаданные трека из Music Catalog
        track = await self._track_service.get_track(track_id=track_id)
        if not track:
            raise TrackNotFoundError("Track not found")
        
        if bitrate not in track.available_bitrates:
            raise ValueError("Unsupported bitrate")

        # Создаем сессию
        session = StreamingSession(
            session_id=self._generate_session_id(),
            user_id=user_id,
            track_id=track_id,
            bitrate=bitrate,
        )

        session.add_event(SessionStartedEvent(
            session_id=session.session_id,
            user_id=user_id,
            track_id=track_id,
            timestamp=datetime.utcnow(),
        ))

        # Сохраняем и публикуем события
        await self.session_repo.save(session)
        for event in session.collect_events():
            await self.event_publisher.publish(event)

        return session.session_id

    def _generate_session_id(self) -> str:
        return f"sess_{uuid.uuid4().hex}"