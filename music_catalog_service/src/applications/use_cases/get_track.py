from src.domain.music_catalog.repository import MusicRepository
from src.domain.cache.cache_repository import CacheRepository, CacheTTL
from src.domain.cache.serialization import CacheSerializer
from src.domain.music_catalog.models import Track

from src.applications.decorators.cache import cached
from src.core.exceptions import TrackNotFound
from src.core.logger import logger

class GetTrackUseCase:
    def __init__(
        self,
        music_repo: MusicRepository,
        cache_repo: CacheRepository,
        cache_serializer: CacheSerializer 
    ):
        self._repo = music_repo
        self._cache_repo = cache_repo
        self._cache_serializer = cache_serializer 


    @cached(ttl=CacheTTL.DEFAULT)
    async def execute(self, track_id: int) -> Track:
        track = await self._repo.get_by_id(track_id=track_id)

        if not track:
            raise TrackNotFound(f"Track_{track_id} not found")

        return track