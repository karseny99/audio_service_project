from functools import wraps
from typing import Callable, Optional, Any, Dict
from src.core.logger import logger
from src.domain.cache.cache_repository import CacheTTL
import json
import inspect
import hashlib

def cached(
    key_template: Optional[str] = None,
    ttl: int = CacheTTL.DEFAULT
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 1. Проверка зависимостей кэширования
            cache_repo = getattr(self, "_cache_repo", None)
            _serializer = getattr(self, "_cache_serializer", None)
            
            if not cache_repo or not _serializer:
                raise AttributeError(f"Cache repository or serializer not found in {self.__class__.__name__}")

            # 2. Поиск объекта запроса в аргументах
            request = None
            for arg in args:
                if hasattr(arg, "dict") and callable(arg.dict):
                    request = arg
                    break
            
            if not request:
                for _, value in kwargs.items():
                    if hasattr(value, "dict") and callable(value.dict):
                        request = value
                        break
            
            # 3. Генерация ключа кэша
            if key_template and request:
                try:
                    # Создаем хеш запроса для уникального ключа
                    request_hash = hashlib.md5(
                        json.dumps(request.dict(), sort_keys=True).encode()
                    ).hexdigest()
                    cache_key = f"{func.__name__}_{request_hash}"
                except Exception as e:
                    logger.warning(f"Key generation error: {e}")
                    cache_key = f"{func.__name__}_fallback_key"
            else:
                # Резервный вариант генерации ключа
                cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"

            # 4. Проверка кэша
            cached_data = await cache_repo.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for key {cache_key}")
                # Получаем тип возвращаемого значения из аннотаций функции
                return_type = func.__annotations__.get("return")
                return _serializer.deserialize(cached_data, return_type)

            # 5. Выполнение функции и кэширование результата
            result = await func(self, *args, **kwargs)
            
            serialized = _serializer.serialize(result)
            await cache_repo.set(cache_key, serialized, ttl)
            logger.debug(f"Cached result for key {cache_key}, ttl={ttl}")
            
            return result

        return wrapper
    return decorator