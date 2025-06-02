from src.domain.user_likes.repository import UserLikesRepository
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
    async def execute(self, user_id: int, track_id: int) -> None:
        await self._likes_repo.add_to_history(user_id=user_id, track_id=track_id)
