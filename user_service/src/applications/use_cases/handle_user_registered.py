# src/application/use_cases/handle_user_registered.py
from src.domain.events.events import UserRegistered
from src.domain.playlists.services import PlaylistService

class HandleUserRegistered:
    def __init__(self, playlist_service: PlaylistService):
        self._playlist_service = playlist_service

    async def __call__(self, event: UserRegistered) -> None:
        await self._playlist_service.create_playlist(
            user_id=event.user_id,
            playlist_name="Favourites"
        )