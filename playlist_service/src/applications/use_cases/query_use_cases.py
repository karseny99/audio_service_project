from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass
from src.domain.playlists.repository import PlaylistRepository
from src.domain.playlists.models import Playlist
from src.domain.playlists.models import PlaylistTrack
from src.core.exceptions import (
    PlaylistNotFoundError,
    InsufficientPermission,
)
from src.core.logger import logger


class GetUserPlaylistsUseCase:
    def __init__(self, playlist_repo: PlaylistRepository):
        self._playlist_repo = playlist_repo

    async def execute(self, user_id: int) -> List[Playlist]:
        playlists = await self._playlist_repo.get_user_playlists(user_id)
        if not playlists:
            logger.debug(f"No playlists found for user {user_id}")
        return playlists

class GetPlaylistTracksUseCase:
    def __init__(self, playlist_repo: PlaylistRepository):
        self._playlist_repo = playlist_repo

    async def execute(self, playlist_id: int, requester_id: Optional[int] = None) -> List[PlaylistTrack]:
        playlist = await self._playlist_repo.get_by_id(playlist_id)
        if not playlist:
            raise PlaylistNotFoundError(f"Playlist {playlist_id} not found")
        
        if not playlist.is_public and playlist.owner_id != requester_id:
            raise InsufficientPermission("No access to this playlist")
        
        return playlist.tracks
