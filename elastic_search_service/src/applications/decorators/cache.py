from functools import wraps
from typing import Callable, Optional, Any, Dict
from src.core.logger import logger
from src.domain.cache.cache_repository import CacheTTL
import json

def cached(
    key_template: Optional[str] = None,
    ttl: int = CacheTTL.DEFAULT
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_repo = getattr(self, "_cache_repo", None)
            _serializer = getattr(self, "_cache_serializer", None)
            
            if not cache_repo or not _serializer:
                raise AttributeError(f"Cache repository or serializer not found in {self.__class__.__name__}")

            if key_template is None:
                cache_key_parts = [
                    self.__class__.__name__,
                    func.__name__,
                    *[str(a) for a in args],
                    *[f"{k}={v}" for k, v in sorted(kwargs.items())]
                ]
                cache_key = ":".join(cache_key_parts)
            else:
                safe_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(v, list):
                        safe_kwargs[k] = ",".join(map(str, v))
                    elif v is None:
                        safe_kwargs[k] = "null"
                    elif hasattr(v, 'isoformat'):  # Для дат
                        safe_kwargs[k] = v.isoformat()
                    else:
                        safe_kwargs[k] = str(v)
                
                safe_args = [str(a) if a is not None else "null" for a in args]
                
                try:
                    cache_key = key_template.format(*safe_args, **safe_kwargs)
                except (KeyError, IndexError) as e:
                    logger.warning(f"Key formatting error: {e}. Using fallback key")
                    cache_key = f"{func.__name__}_fallback_key"

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