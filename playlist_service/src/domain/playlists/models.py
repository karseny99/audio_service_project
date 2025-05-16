from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.domain.playlists.value_objects import PlaylistTitle, TrackId, UserId
from src.core.exceptions import TrackAlreadyInPlaylist

@dataclass(frozen=True)
class PlaylistTrack:
    track_id: TrackId
    position: int
    added_at: datetime

@dataclass(frozen=False)
class Playlist:
    playlist_id: int
    name: PlaylistTitle
    owner_id: UserId
    is_public: bool = False
    created_at: datetime = datetime.utcnow()
    tracks: List[PlaylistTrack] = field(default_factory=list)
    
    def add_track(self, track_id: TrackId, position: Optional[int] = None) -> None:
        """Добавляет трек с автоматической датой и позицией"""
        added_at = datetime.utcnow()
        
        if position is None:
            position = len(self.tracks)
        
        new_track = PlaylistTrack(
            track_id=track_id,
            position=position,
            added_at=added_at
        )
        
        # Проверка уникальности трека
        if any(t.track_id == track_id for t in self.tracks):
            raise TrackAlreadyInPlaylist("Трек уже в плейлисте")
            
        self.tracks.append(new_track)
        self._reorder_positions()

    def _reorder_positions(self) -> None:
        """Гарантирует последовательные позиции после изменений"""
        self.tracks.sort(key=lambda x: x.position)
        for idx, track in enumerate(self.tracks):
            track.position = idx