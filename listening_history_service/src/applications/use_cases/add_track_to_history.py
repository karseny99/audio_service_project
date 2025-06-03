from src.domain.user_likes.repository import UserLikesRepository
from src.domain.events.events import TrackListened
from src.domain.tracks.services import AbstractTrackService
from src.core.exceptions import (
    TrackNotFoundError,
)
from src.core.logger import logger

class HandleTrackListenedUseCase:
    def __init__(
        self,
        likes_repo: UserLikesRepository,
    ):
        self._likes_repo = likes_repo
    async def execute(self, event: TrackListened) -> None:
        
        # skip if sent less than 50% 
        if event.total_chunks_sent < event.total_chunks * 0.5:
            logger.info(f"Track_{event.track_id} wasn't added: listened for {event.total_chunks_sent / event.total_chunks * 100:.1f}%")
            return

        logger.info(f"Track_{event.track_id} added: listened for {event.total_chunks_sent / event.total_chunks * 100:.1f}%")
        await self._likes_repo.add_to_history(user_id=event.user_id, track_id=event.track_id, timestamp=event.timestamp)
