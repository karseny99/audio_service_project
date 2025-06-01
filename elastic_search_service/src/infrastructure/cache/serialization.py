import json
from datetime import date, datetime
from typing import Any, Type
from pydantic import BaseModel
import logging 

logger = logging.getLogger(__name__)

class DomainJsonSerializer:
    def serialize(self, obj: Any) -> bytes:
        if isinstance(obj, BaseModel):
            return obj.json().encode("utf-8")
        return json.dumps(obj).encode("utf-8")

    def deserialize(self, data: bytes, target_type: Type = None) -> Any:
        if data == b"null":
            return None
        
        decoded = json.loads(data.decode("utf-8"))
        
        if target_type and issubclass(target_type, BaseModel):
            try:
                return target_type.parse_obj(decoded)
            except Exception as e:
                logger.error(f"Deserialization error: {str(e)}")
                return decoded
        return decoded