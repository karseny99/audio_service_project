from typing import Optional

from src.core.logger import logger

from src.infrastructure.cache.redis_client import RedisClient

class RedisCacheRepository:
    def __init__(self, redis: RedisClient):
        self._redis = redis
    
    async def get(self, key: str) -> Optional[str]:
        try:
            return await self._redis.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, ttl: int) -> None:
        try:
            await self._redis.client.set(key, value, ex=ttl)
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
    
    async def delete(self, key: str) -> None:
        try:
            await self._redis.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {str(e)}")