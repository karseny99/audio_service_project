from src.domain.playlists.repository import PlaylistRepository
from src.domain.events.events import TrackAddedToPlaylist 
from src.domain.tracks.services import AbstractTrackService
from src.domain.events.publisher import EventPublisher
from src.core.exceptions import (
    TrackNotFoundError,
    InsufficientPermission,
)  
from src.core.logger import logger



class AddTrackToPlaylistUseCase:
    def __init__(
        self,
        playlist_repo: PlaylistRepository,
        track_service: AbstractTrackService,
        event_publisher: EventPublisher,
    ):
        self._playlist_repo = playlist_repo
        self._track_service = track_service
        self._event_publisher = event_publisher

    async def execute(self, playlist_id: str, track_id: str, user_id: str) -> None:
        track_exists = await self._track_service.verify_track_exists(track_id)
        if not track_exists:
            raise TrackNotFoundError(f"Track {track_id} not found")
        
        actual_owner = await self._playlist_repo.get_playlist_owner(playlist_id)
        if actual_owner.id != user_id:
            raise InsufficientPermission(f"User {user_id} does not have such rights")

        playlist = await self._playlist_repo.get_by_id(playlist_id)
        playlist.add_track(track_id)
        await self._playlist_repo.update(playlist)
        
        await self._event_publisher.publish(
            event=TrackAddedToPlaylist(
                playlist_id=playlist_id,
                track_id=track_id,
                user_id=user_id
            ),
            key=str(playlist.playlist_id)
        )

