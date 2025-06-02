from src.domain.user_likes.repository import UserLikesRepository
from src.core.exceptions import (
    TrackNotFoundError,
)
from src.core.logger import logger


class GetUserLikesUseCase:
    def __init__(
        self,
        likes_repo: UserLikesRepository,
    ):
        self._likes_repo = likes_repo

    async def execute(self, user_id: int, count: int, offset: int):
        likes = await self._likes_repo.get_user_likes(user_id=user_id)
        
        return [ like.track_id for like in likes[offset:offset + count] ]
