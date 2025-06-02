import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.like_track import LikeTrackUseCase
from src.core.exceptions import TrackNotFoundError
from src.domain.tracks.services import AbstractTrackService
from src.domain.user_likes.repository import UserLikesRepository

class TestLikeTrackUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        # Создаем моки для зависимостей
        self.mock_likes_repo = AsyncMock(spec=UserLikesRepository)
        self.mock_track_service = MagicMock(spec=AbstractTrackService)
        
        # Создаем экземпляр UseCase с моками
        self.use_case = LikeTrackUseCase(
            likes_repo=self.mock_likes_repo,
            track_service=self.mock_track_service
        )
    
    async def test_like_track_success(self):
        """Успешное добавление лайка"""
        user_id = 1
        track_id = 42
        
        # Настраиваем track_service: трек существует
        self.mock_track_service.verify_track_exists.return_value = True
        
        # Выполняем UseCase
        await self.use_case.execute(user_id, track_id)
        
        # Проверяем вызовы зависимостей
        self.mock_track_service.verify_track_exists.assert_called_once_with(track_id)
        self.mock_likes_repo.add_like.assert_awaited_once_with(
            user_id=user_id, 
            track_id=track_id
        )
    
    async def test_like_track_track_not_found(self):
        """Попытка лайка несуществующего трека"""
        user_id = 1
        track_id = 999
        
        # Настраиваем track_service: трек не существует
        self.mock_track_service.verify_track_exists.return_value = False
        
        # Ожидаем исключение
        with pytest.raises(TrackNotFoundError) as exc_info:
            await self.use_case.execute(user_id, track_id)
        
        # Проверяем текст исключения
        assert f"Track {track_id} not found" in str(exc_info.value)
        
        # Проверяем, что verify был вызван, а add_like - нет
        self.mock_track_service.verify_track_exists.assert_called_once_with(track_id)
        self.mock_likes_repo.add_like.assert_not_called()