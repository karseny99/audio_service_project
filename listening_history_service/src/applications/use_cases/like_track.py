from dependency_injector.wiring import inject, Provide

from src.domain.user_likes.repository import UserLikesRepository
from src.domain.tracks.services import AbstractTrackService
from src.core.exceptions import (
    TrackNotFoundError,
    TrackAlreadyLiked
)
from src.core.logger import logger


class LikeTrackUseCase:
    # @inject
    def __init__(
        self,
        likes_repo: UserLikesRepository,
        track_service: AbstractTrackService,
    ):
        self._likes_repo = likes_repo
        self._track_service = track_service

    async def execute(self, user_id: int, track_id: int) -> None:
        # Проверяем, что трек существует
        # track_exists = await self._track_service.verify_track_exists(track_id)
        # if not track_exists:
        #     raise TrackNotFoundError(f"Track {track_id} not found")

        
        await self._likes_repo.add_like(user_id=user_id, track_id=track_id)
