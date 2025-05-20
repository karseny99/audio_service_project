from abc import ABC, abstractmethod
from google.protobuf.message import Message
from typing import Generic, TypeVar

T = TypeVar('T', bound=Message)

class EventHandler(ABC, Generic[T]):
    @abstractmethod
    async def handle(self, event: T, container: 'Container') -> None:
        raise NotImplementedError