from abc import ABC, abstractmethod

class EventUseCase(ABC):
    @abstractmethod
    async def execute(self, event) -> None:
        raise NotImplementedError
