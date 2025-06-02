from src.domain.users.repository import UserRepository
from src.domain.cache.cache_repository import CacheRepository, CacheTTL
from src.domain.cache.serialization import CacheSerializer

from src.applications.decorators.cache import cached

from src.core.exceptions import UserNotFoundError, InvalidPasswordError
from src.core.logger import logger

class AuthUserUseCase:
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
    async def execute(self, username: str, password: str) -> str:
        
        logger.debug(f"{username} tries to log in")

        user = await self._repo.get_by_username(username)
        if user is None:
            logger.debug(f"{username} doesn't exists")
            raise UserNotFoundError(f"User {username} does not exists")

        logger.debug(f"{user.password_hash.value}")
        if password != user.password_hash.value:
            logger.debug(f"Invalid password")
            raise InvalidPasswordError(f"Invalid credentials")
        
        logger.debug(f"Successfully logged in")
        return str(user.id)