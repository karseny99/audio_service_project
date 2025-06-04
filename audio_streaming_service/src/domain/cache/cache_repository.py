from abc import ABC, abstractmethod
from typing import Optional

class CacheTTL:
    UNPOPULAR = 600
    DEFAULT = 30
    POPULAR = 86400

class CacheRepository(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: bytes, ttl: int) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass