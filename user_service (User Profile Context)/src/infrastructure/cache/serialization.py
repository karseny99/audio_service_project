import json
from datetime import date, datetime
from dataclasses import is_dataclass, asdict
from typing import Any, Type

from src.domain.cache.serialization import CacheSerializer

class DomainJsonSerializer(CacheSerializer):
    def serialize(self, obj: Any) -> bytes:
        if obj is None:
            return b'null'
        
        def default_serializer(o):
            if isinstance(o, (datetime, date)):
                return o.isoformat()
            if hasattr(o, '__dict__'):
                return vars(o)
            raise TypeError(f"Object of type {type(o)} is not JSON serializable")
        
        return json.dumps(obj, default=default_serializer).encode('utf-8')

    def deserialize(self, data: bytes, target_type: Type) -> Any:
        if data == b'null':
            return None
        
        decoded = json.loads(data.decode('utf-8'))
        
        if target_type is dict:
            return decoded
            
        if is_dataclass(target_type):
            return target_type(**decoded)
            
        return decoded