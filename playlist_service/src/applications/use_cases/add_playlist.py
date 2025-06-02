from src.domain.playlists.repository import PlaylistRepository, PlaylistSubscriptionRepository
from src.core.exceptions import PlaylistNotFoundError, InsufficientPermission
from src.core.logger import logger


class AddPlaylistUseCase:
    def __init__(
        self,
        playlist_repo: PlaylistRepository,
        subscription_repo: PlaylistSubscriptionRepository,
    ):
        self._playlist_repo = playlist_repo
        self._subscription_repo = subscription_repo

    async def execute(self, playlist_id: int, user_id: str) -> None:
        playlist = await self._playlist_repo.get_by_id(playlist_id)
        if playlist is None:
            raise PlaylistNotFoundError(f"Playlist {playlist_id} not found")

        if not playlist.is_public:
            raise InsufficientPermission("Cannot subscribe to a private playlist")

        is_subscribed = await self._subscription_repo.is_subscribed(user_id, playlist_id)
        if is_subscribed:
            logger.info(f"User {user_id} is already subscribed to playlist {playlist_id}")
            return

        await self._subscription_repo.add_subscription(user_id, playlist_id)
        logger.info(f"User {user_id} subscribed to playlist {playlist_id}")
