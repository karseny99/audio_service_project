import uuid
import json
import pickle
from datetime import datetime
from typing import Optional
from uuid import UUID
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
import asyncio

from src.core.logger import logger
from src.core.exceptions import (
    SessionDeserializationError,
    SessionSerializationError,
    SessionRepositoryError,
)

from src.domain.stream.models import StreamSession, AudioTrack, StreamStatus
from src.domain.stream.repository import StreamingRepository
from src.infrastructure.database.redis_client import RedisClient

class CacheTTL:
    UNPOPULAR = 600
    DEFAULT = 1800      # 30 min
    POPULAR = 86400

class RedisStreamingRepository(StreamingRepository):
    def __init__(self, redis_client: RedisClient, ttl_seconds: int = CacheTTL.DEFAULT):
        """
        :param redis_client: клиент Redis
        :param ttl_seconds: время жизни сессии в секундах (по умолчанию полчаса)
        """
        self._redis = redis_client
        self._ttl = ttl_seconds

    def _serialize_session(self, session: StreamSession) -> bytes:
        """Сериализация сессии в bytes для Redis, исключая несериализуемые поля"""
        try:
            # Создаем копию данных, исключая несериализуемые поля
            session_dict = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'current_bitrate': session.current_bitrate,
                'chunk_size': session.chunk_size,
                'status': session.status.name,
                'current_chunk': session.current_chunk,
                'started_at': session.started_at.isoformat(),
                'track': {
                    'track_id': session.track.track_id,
                    'total_chunks': session.track.total_chunks,
                    'available_bitrates': session.track.available_bitrates,
                    'duration_ms': session.track.duration_ms
                }
            }
            
            # Добавляем опциональные поля
            if session.paused_at:
                session_dict['paused_at'] = session.paused_at.isoformat()
            if session.finished_at:
                session_dict['finished_at'] = session.finished_at.isoformat()
            
            return json.dumps(session_dict).encode('utf-8')
        except Exception as e:
            logger.error(f"Session serialization error: {str(e)}")
            raise SessionSerializationError("Failed to serialize session")

    def _deserialize_session(self, data: bytes) -> Optional[StreamSession]:
        if not data:
            return None
            
        try:
            session_dict = json.loads(data.decode('utf-8'))
            
            # Восстановление объекта Track
            track = AudioTrack(
                track_id=session_dict['track']['track_id'],
                total_chunks=session_dict['track']['total_chunks'],
                available_bitrates=session_dict['track']['available_bitrates'],
                duration_ms=session_dict['track']['duration_ms']
            )
            
            # Восстановление сессии
            session = StreamSession(
                session_id=session_dict['session_id'],
                user_id=session_dict['user_id'],
                track=track,
                chunk_size=session_dict['chunk_size'],
                current_bitrate=session_dict['current_bitrate'],
                status=StreamStatus[session_dict['status']],
                current_chunk=session_dict['current_chunk'],
                started_at=datetime.fromisoformat(session_dict['started_at'])
            )
            
            # Восстановление опциональных полей
            if 'paused_at' in session_dict:
                session.paused_at = datetime.fromisoformat(session_dict['paused_at'])
            if 'finished_at' in session_dict:
                session.finished_at = datetime.fromisoformat(session_dict['finished_at'])
            
            # Несериализуемые поля инициализируем заново
            session.message_queue = asyncio.Queue()
            session.reader_task = None
            
            return session
        except Exception as e:
            logger.error(f"Session deserialization error: {str(e)}")
            raise SessionDeserializationError("Failed to deserialize session")

    def _get_redis_key(self, session_id: str) -> str:
        """Генерирует ключ для Redis"""
        return f"stream_session:{session_id}"

    async def get(self, session_id: UUID) -> Optional[StreamSession]:
        """Получить сессию по ID"""
        try:
            key = self._get_redis_key(session_id)
            data = await self._redis.client.get(key)
            return self._deserialize_session(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            raise SessionRepositoryError("Failed to get session")

    async def save(self, session: StreamSession) -> None:
        """Сохранить или обновить сессию"""
        try:
            key = self._get_redis_key(session.session_id)
            data = self._serialize_session(session)
            await self._redis.client.set(key, data, ex=self._ttl)
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {str(e)}")
            raise SessionRepositoryError("Failed to save session")

    async def delete(self, session_id: UUID) -> bool:
        """Удалить сессию (возвращает True если сессия существовала)"""
        try:
            key = self._get_redis_key(session_id)
            deleted = await self._redis.client.delete(key)
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise SessionRepositoryError("Failed to delete session")

    async def cleanup_expired_sessions(self) -> int:
        """Очистка просроченных сессий (Redis делает это автоматически)"""
        logger.info("Redis handles expiration automatically via TTL")
        return 0
