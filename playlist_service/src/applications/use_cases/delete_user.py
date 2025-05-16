from src.domain.playlists.repository import PlaylistRepository
from src.domain.events.events import UserDeleted
from src.core.logger import logger


class HandleUserDeletedUseCase:
    def __init__(self, playlist_repo: PlaylistRepository):
        self._playlist_repo = playlist_repo

    async def execute(self, event: UserDeleted) -> None:
        """Удаляет все плейлисты пользователя"""

        logger.info(f"Starting execution of {event}")

        total_deleted = await self._playlist_repo.delete_user_playlist_relations(event.user_id)
               
        logger.info(
            f"""Deleted {total_deleted} playlists for user {event.user_id}"""
        )