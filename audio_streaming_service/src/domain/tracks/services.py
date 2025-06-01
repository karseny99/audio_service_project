from abc import ABC, abstractmethod

class AbstractTrackService(ABC):
    """Абстракция для сервиса проверки треков"""
    
    @abstractmethod
    async def get_track(self, track_id: str) -> bool:
        raise NotImplementedError