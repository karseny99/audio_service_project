from src.domain.playlists.repository import PlaylistRepository
from src.domain.playlists.models import Playlist
from src.domain.events.events import TrackAddedToPlaylist 
from src.domain.tracks.services import AbstractTrackService
from src.domain.events.publisher import EventPublisher
from src.core.exceptions import (
    TrackNotFoundError,
    InsufficientPermission,
)  
from src.core.logger import logger
class CreatePlaylistUseCase:
    def __init__(
        self,
        playlist_repo: PlaylistRepository,
    ):
        self._playlist_repo = playlist_repo

    async def execute(self, user_id: int, title: str) -> int:
        playlist = await self._playlist_repo.create_playlist(title, user_id, True)
        return playlist.playlist_id