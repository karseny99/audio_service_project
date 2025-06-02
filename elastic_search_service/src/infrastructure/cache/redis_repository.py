from typing import Optional
from src.core.logger import logger
from src.infrastructure.cache.redis_client import RedisClient
from src.domain.cache.cache_repository import CacheRepository

class RedisCacheRepository(CacheRepository):
    def __init__(self, redis: RedisClient):
        self._redis = redis

    async def get(self, key: str) -> Optional[bytes]:
        try:
            return await self._redis.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(self, key: str, value: bytes, ttl: int) -> None:
        try:
            await self._redis.client.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")

    async def delete(self, key: str) -> None:
        try:
            await self._redis.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
