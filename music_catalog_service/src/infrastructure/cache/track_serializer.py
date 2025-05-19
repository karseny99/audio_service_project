
from datetime import datetime, date
from typing import Type, Optional
import json 

from src.core.logger import logger
from src.domain.cache.serialization import CacheSerializer
from src.domain.music_catalog.models import (
    ArtistInfo, 
    Genre, 
    DurationMs, 
    Track
)

class TrackSerializer(CacheSerializer):
    def __init__(self, base_serializer: CacheSerializer):
        self._base = base_serializer

    def serialize(self, track: Optional['Track']) -> bytes:
        if track is None:
            return self._base.serialize(None)
        
        # Преобразуем track в словарь
        track_dict = {
            'track_id': track.track_id,
            'title': track.title,
            'duration': track.duration,
            'artists': [vars(a) for a in track.artists],
            'genres': [vars(g) for g in track.genres],
            'explicit': track.explicit,
            'release_date': track.release_date,
            'created_at': track.created_at
        }
        return self._base.serialize(track_dict)

    def deserialize(self, data: bytes, target_type: Type[Optional['Track']]) -> Optional['Track']:
        if data is None:
            return None
            
        decoded = self._base.deserialize(data, dict)
        
        if decoded is None:
            return None
            
        # Десериализуем artists и genres
        artists = [ArtistInfo(**a) for a in decoded['artists']]
        genres = [Genre(**g) for g in decoded['genres']]
        
        return target_type(
            track_id=int(decoded['track_id']),
            title=decoded['title'],
            duration=DurationMs(value=int(decoded['duration'])),
            artists=artists,
            genres=genres,
            explicit=bool(decoded['explicit']),
            release_date=date.fromisoformat(decoded['release_date']) if decoded['release_date'] else None,
            created_at=datetime.fromisoformat(decoded['created_at']) if decoded['created_at'] else None
        )
