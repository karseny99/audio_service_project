from functools import wraps
from typing import Callable, Optional

from src.domain.cache.serialization import CacheSerializer
from src.domain.cache.cache_repository import CacheTTL
from src.core.logger import logger


from functools import wraps
from typing import Callable, Optional
from src.domain.cache.cache_repository import CacheTTL

def cached(
    key_template: Optional[str] = None,
    ttl: int = CacheTTL.DEFAULT
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_repo = self._cache_repo
            _serializer = self._cache_serializer
            
            if not cache_repo:
                raise AttributeError(f"Cache repository not found in {self.__class__.__name__}")
            
            # Формирование ключа
            if key_template is None:
                class_name = self.__class__.__name__
                args_str = ":".join(str(arg) for arg in args)
                kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{class_name}:{func.__name__}:{args_str}:{kwargs_str}"
            else:
                cache_key = key_template.format(*args, **kwargs)
            
            # Проверка кэша
            cached_data = await cache_repo.get(cache_key)
            if cached_data is not None:
                return_type = func.__annotations__.get('return')
                return _serializer.deserialize(cached_data, return_type)
            
            # Выполнение и кэширование
            result = await func(self, *args, **kwargs)
            await cache_repo.set(
                cache_key, 
                _serializer.serialize(result), 
                ttl
            )
            
            return result
        return wrapper
    return decorator
