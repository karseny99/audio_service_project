from abc import ABC, abstractmethod
from typing import Any, Type

class CacheSerializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, data: bytes, target_type: Type) -> Any:
        raise NotImplementedError
