# src/applications/decorators/cache.py

from functools import wraps
from typing import Callable, Optional

from src.domain.cache.serialization import CacheSerializer
from src.domain.cache.cache_repository import CacheTTL
from src.core.logger import logger


def cached(
    key_template: Optional[str] = None,
    ttl: int = CacheTTL.DEFAULT
):
    """
    Декоратор для асинхронного кеширования результата вызова метода.
    Ожидается, что в классе, где применяется декоратор, есть атрибуты:
      - self._cache_repo: экземпляр CacheRepository
      - self._cache_serializer: экземпляр CacheSerializer
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_repo = getattr(self, "_cache_repo", None)
            _serializer = getattr(self, "_cache_serializer", None)

            if not cache_repo or not _serializer:
                raise AttributeError(f"Cache repository or serializer not found in {self.__class__.__name__}")

            if key_template is None:
                class_name = self.__class__.__name__
                args_str = ":".join(str(a) for a in args)
                kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{class_name}:{func.__name__}:{args_str}:{kwargs_str}"
            else:
                cache_key = key_template.format(*args, **kwargs)

            cached_data = await cache_repo.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for key {cache_key}")
                return _serializer.deserialize(cached_data, func.__annotations__.get("return"))

            result = await func(self, *args, **kwargs)
            serialized = _serializer.serialize(result)
            await cache_repo.set(cache_key, serialized, ttl)
            logger.debug(f"Cached result for key {cache_key}, ttl={ttl}")
            return result

        return wrapper
    return decorator
