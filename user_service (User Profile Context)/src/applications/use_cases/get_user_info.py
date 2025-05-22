from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from src.domain.users.repository import UserRepository
from src.domain.cache.cache_repository import CacheRepository, CacheTTL
from src.domain.cache.serialization import CacheSerializer

from src.applications.decorators.cache import cached
from src.core.exceptions import UserNotFoundError

from src.core.logger import logger

class GetUserInfoUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        cache_repo: CacheRepository,
        cache_serializer: CacheSerializer,
    ):
        self._repo = user_repo
        self._cache_repo = cache_repo
        self._cache_serializer = cache_serializer

    @cached(ttl=CacheTTL.DEFAULT)
    async def execute(self, user_id: str) -> dict:
        logger.debug(f"Fetching info for user {user_id}")

        user = await self._repo.get_by_id(user_id)
        if user is None:
            logger.warning(f"User {user_id} not found")
            raise UserNotFoundError(f"User {user_id} does not exist")

        created_at = Timestamp()
        created_at.FromDatetime(user.created_at)

        return {
            "username": user.username,
            "email": user.email,
            "created_at": created_at
        }