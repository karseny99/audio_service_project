from abc import ABC, abstractmethod

class AbstractTrackService(ABC):
    """Абстракция для сервиса проверки треков"""
    
    @abstractmethod
    async def verify_track_exists(self, track_id: str) -> bool:
        raise NotImplementedError