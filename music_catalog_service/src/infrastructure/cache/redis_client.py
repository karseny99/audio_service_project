import redis.asyncio as redis
from typing import Optional, Any
import asyncio

from src.core.config import settings
from src.core.logger import logger


class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._redis = None
            cls._instance._url = settings.REDIS_URL
        return cls._instance
    
    async def connect(self):
        if self._redis is None:
            self._redis = redis.from_url(
                self._url,
                encoding="utf-8",
                decode_responses=False
            )
            logger.info(f"Connected to Redis at {self._url}")
    
    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[bytes]:
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, ex: int = None) -> None:
        await self._redis.set(key, value, ex=ex)

    @property
    def client(self):
        if not self._redis:
            raise RuntimeError("Redis client not connected")
        return self._redis