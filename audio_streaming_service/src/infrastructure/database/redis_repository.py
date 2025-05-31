import uuid
import json
import pickle
from datetime import datetime
from typing import Optional
from uuid import UUID
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass

from src.core.logger import logger
from src.core.exceptions import (
    SessionDeserializationError,
    SessionSerializationError,
    SessionRepositoryError,
)

from src.domain.stream.models import StreamSession
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
        """Сериализация сессии в bytes для Redis"""
        try:
            session_dict = asdict(session)
            
            session_dict['started_at'] = session.started_at.isoformat()
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
            
            session_dict['started_at'] = datetime.fromisoformat(session_dict['started_at'])
            if session_dict.get('paused_at'):
                session_dict['paused_at'] = datetime.fromisoformat(session_dict['paused_at'])
            if session_dict.get('finished_at'):
                session_dict['finished_at'] = datetime.fromisoformat(session_dict['finished_at'])
            
            return StreamSession(**session_dict)
        except Exception as e:
            logger.error(f"Session deserialization error: {str(e)}")
            raise SessionDeserializationError("Failed to deserialize session")

    def _get_redis_key(self, session_id: UUID) -> str:
        """Генерирует ключ для Redis"""
        return f"stream_session:{session_id.hex}"

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
