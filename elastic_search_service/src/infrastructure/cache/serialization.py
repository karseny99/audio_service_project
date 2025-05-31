# src/infrastructure/cache/serialization.py

import json
from datetime import date, datetime
from typing import Any, Type
from dataclasses import is_dataclass

from src.domain.cache.serialization import CacheSerializer

class DomainJsonSerializer(CacheSerializer):
    def serialize(self, obj: Any) -> bytes:
        if obj is None:
            return b"null"

        def default(o):
            if isinstance(o, (date, datetime)):
                return o.isoformat()
            if is_dataclass(o):
                return o.__dict__
            if hasattr(o, "__dict__"):
                return o.__dict__
            raise TypeError(f"Type {type(o)} not JSON serializable")

        return json.dumps(obj, default=default).encode("utf-8")

    def deserialize(self, data: bytes, target_type: Type) -> Any:
        if data == b"null":
            return None
        decoded = json.loads(data.decode("utf-8"))
        # В этом сервисе мы можем возвращать простой словарь или список словарей
        return decoded
