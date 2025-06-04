from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.music_catalog.models import Track, ArtistInfo, Genre

class MusicRepository(ABC):
    @abstractmethod
    async def get_by_id(self, track_id: int) -> Optional[Track]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_artist(
        self, artist_id: int, offset: int = 0, limit: int = 50
    ) -> List[Track]:
        '''returns tracks by given artist'''
        raise NotImplementedError

    @abstractmethod
    async def get_by_genre(self, genre_id: int, offset: int = 0, limit: int = 50) -> List[Track]:
        '''returns tracks by given genre with pagination'''
        raise NotImplementedError

    @abstractmethod
    async def add(self, track: Track) -> Track:
        raise NotImplementedError

    @abstractmethod
    async def update(self, track: Track) -> None:
        raise NotImplementedError