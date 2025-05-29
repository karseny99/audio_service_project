from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator
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

    # # === Чанки === #
    # @abstractmethod
    # async def get_chunk(
    #     self,
    #     track_id: str,
    #     chunk_number: int,
    #     bitrate: str
    # ) -> Optional[AudioChunk]:
    #     """Получить аудио-чанк по номеру и битрейту"""
    #     raise NotImplementedError


class AbstractTrackService(ABC):
    """Абстракция для сервиса проверки треков"""
    
    @abstractmethod
    async def get_track(self, track_id: str) -> Optional[AudioTrack]:
        """Получить метаданные трека"""
        raise NotImplementedError


class AudioStorage(ABC):
    """Абстракция для хранилища аудио-данных."""
    
    @abstractmethod
    async def get_chunks(
        self, 
        track_id: str, 
        bitrate: int, 
        offset: int = 0,
        chunk_size: int = 1024 * 64
    ) -> AsyncGenerator[bytes, None]:
        """Генератор чанков аудио."""
        raise NotImplementedError