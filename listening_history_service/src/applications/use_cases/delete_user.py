from src.domain.user_likes.repository import UserLikesRepository
from src.domain.events.events import UserDeleted
from src.core.logger import logger


class HandleUserDeletedUseCase:
    def __init__(self, likes_repo: UserLikesRepository,):
        self._likes_repo = likes_repo

    async def execute(self, event: UserDeleted) -> None:

        logger.info(f"Starting execution of {event}")

        await self._likes_repo.remove_likes(event.user_id)
               
        logger.info(
            f"""Deleted all likes for user {event.user_id}"""
        )