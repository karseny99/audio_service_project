from src.domain.music_catalog.repository import MusicRepository
from src.domain.cache.cache_repository import CacheRepository, CacheTTL
from src.domain.cache.serialization import CacheSerializer
from src.applications.decorators.cache import cached
from src.core.logger import logger
from typing import List
from src.domain.music_catalog.models import Track

class GetTracksByArtistUseCase:
    def __init__(
        self,
        music_repo: MusicRepository,
        cache_repo: CacheRepository,
        cache_serializer: CacheSerializer
    ):
        self._repo = music_repo
        self._cache_repo = cache_repo
        self._cache_serializer = cache_serializer

    @cached(key_template="tracks:artist:{artist_id}:{offset}:{limit}")
    async def execute(self, artist_id: int, offset: int = 0, limit: int = 50) -> List[Track]:
        return await self._repo.get_by_artist(artist_id, offset, limit)

class GetTracksByGenreUseCase:
    def __init__(
        self,
        music_repo: MusicRepository,
        cache_repo: CacheRepository,
        cache_serializer: CacheSerializer
    ):
        self._repo = music_repo
        self._cache_repo = cache_repo
        self._cache_serializer = cache_serializer

    @cached(key_template="tracks:genre:{genre_id}:{offset}:{limit}")
    async def execute(self, genre_id: int, offset: int = 0, limit: int = 50) -> List[Track]:
        return await self._repo.get_by_genre(genre_id, offset, limit)