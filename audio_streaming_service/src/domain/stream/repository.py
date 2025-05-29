from abc import ABC, abstractmethod
from typing import Optional, Generator, Union
from uuid import UUID
from datetime import datetime

from .models import (
    StreamSession,
    AudioTrack,
    AudioChunk,
    StreamStatus,
)

class StreamingRepository(ABC):
    """Абстрактный репозиторий для управления стриминговыми сессиями"""
    
    @abstractmethod
    async def get(self, session_id: UUID) -> Optional[StreamSession]:
        """Получить сессию по ID"""
        raise NotImplementedError

    @abstractmethod
    async def save(self, session: StreamSession) -> None:
        """Сохранить или обновить сессию"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Удалить сессию (возвращает True если сессия существовала)"""
        raise NotImplementedError


class AbstractTrackService(ABC):
    """Абстракция для сервиса треков"""
    
    @abstractmethod
    async def get_track(self, track_id: str) -> Optional[AudioTrack]:
        """Получить метаданные трека"""
        raise NotImplementedError


class AudioStreamer(ABC):
    
    @abstractmethod
    def chunks(
        self, 
        start_pos: Union[int, float] = 0
    ) -> Generator[AudioChunk, None, None]:
        """Генератор чанков трека"""
        raise NotImplementedError