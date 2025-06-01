import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.get_user_info import GetUserInfoUseCase
from src.domain.users.models import User
from src.core.exceptions import UserNotFoundError

class TestGetUserInfoUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_user_repo = AsyncMock()
        self.mock_cache_repo = AsyncMock()  # Исправлено на AsyncMock
        self.mock_cache_serializer = MagicMock()
        self.mock_logger = MagicMock()

        # Патчим логгер по месту использования в use case
        self.patcher_logger = patch(
            "src.applications.use_cases.get_user_info.logger",
            self.mock_logger
        )
        self.patcher_logger.start()

        self.use_case = GetUserInfoUseCase(
            user_repo=self.mock_user_repo,
            cache_repo=self.mock_cache_repo,
            cache_serializer=self.mock_cache_serializer
        )
        
        # Настраиваем поведение кэша: всегда возвращаем None (кеш пуст)
        self.mock_cache_repo.get.return_value = None
    
    def tearDown(self):
        self.patcher_logger.stop()
    
    async def test_successful_user_fetch(self):
        """Успешное получение информации о пользователе"""
        user_id = 1
        mock_user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            password_hash="hash"
        )
        
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        result = await self.use_case.execute(user_id)
        
        self.mock_user_repo.get_by_id.assert_awaited_once_with(user_id)
        self.mock_logger.debug.assert_called_once_with(
            f"Fetching info for user {user_id}"
        )
        self.assertEqual(result, mock_user)
    
    async def test_user_not_found(self):
        """Обработка случая, когда пользователь не найден"""
        user_id = 999
        
        self.mock_user_repo.get_by_id.return_value = None
        
        with pytest.raises(UserNotFoundError) as exc_info:
            await self.use_case.execute(user_id)
        
        assert f"User {user_id} does not exist" in str(exc_info.value)
        self.mock_user_repo.get_by_id.assert_awaited_once_with(user_id)
        self.mock_logger.warning.assert_called_once_with(
            f"User {user_id} not found"
        )