from abc import ABC, abstractmethod, abstractproperty
from typing import Optional, AsyncGenerator, Union, List
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
    async def get(self, session_id: str) -> Optional[StreamSession]:
        """Получить сессию по ID"""
        raise NotImplementedError

    @abstractmethod
    async def save(self, session: StreamSession) -> None:
        """Сохранить или обновить сессию"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
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
    async def initialize(self, track_id: str, initial_bitrate: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_bitrates(self) -> List[str]:
        raise NotImplementedError
    
    @abstractmethod
    async def switch_bitrate(self, new_bitrate: str):
        raise NotImplementedError

    @abstractmethod
    def seek(self, offset_bytes: int): 
        raise NotImplementedError
    
    @abstractmethod
    async def chunks(
        self, 
        start_pos: Union[int, float, None]
    ) -> AsyncGenerator[AudioChunk, None]:
        """Генератор чанков трека"""
        raise NotImplementedError
    
    @abstractproperty
    def bitrate(self) -> str:
        """Возвращает текущий битрейт"""
        raise NotImplementedError

    @abstractproperty
    def duration(self) -> float:
        """Возвращает длительность трека в секундах"""
        raise NotImplementedError
    
    @abstractproperty
    def total_chunks(self) -> int:
        raise NotImplementedError
        
    @abstractproperty
    def chunk_size(self) -> int:
        raise NotImplementedError
