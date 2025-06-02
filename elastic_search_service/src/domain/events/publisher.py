from typing import Protocol, runtime_checkable

@runtime_checkable
class EventPublisher(Protocol):
    @abstractmethod
    async def publish(self, event, topic: str, key: str | None = None):
        pass

    @property
    @abstractmethod
    def destination(self) -> str:
        pass
