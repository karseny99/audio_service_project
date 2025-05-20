from abc import ABC, abstractmethod
from google.protobuf.message import Message

class EventUseCase(ABC):
    @abstractmethod
    async def execute(self, event: Message) -> None:
        raise NotImplementedError
