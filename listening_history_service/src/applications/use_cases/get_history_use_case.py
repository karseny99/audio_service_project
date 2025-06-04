from src.domain.user_likes.repository import UserLikesRepository
from src.core.exceptions import (
    TrackNotFoundError,
)
from src.core.logger import logger


class GetHistoryUseCase:
    def __init__(
        self,
        likes_repo: UserLikesRepository,
    ):
        self._likes_repo = likes_repo

    async def execute(self, user_id: int, count: int, offset: int):
        return await self._likes_repo.get_history(user_id=user_id, count=count, offset=offset)
