import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.auth_user import AuthUserUseCase
from src.core.exceptions import UserNotFoundError, InvalidPasswordError
from src.core.logger import logger

class TestAuthUserUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_user_repo = AsyncMock()
        self.mock_cache_repo = AsyncMock()
        self.mock_cache_serializer = MagicMock()
        
        self.patcher_logger = patch("src.applications.use_cases.auth_user.logger", MagicMock())
        self.mock_logger = self.patcher_logger.start()
        
        self.use_case = AuthUserUseCase(
            user_repo=self.mock_user_repo,
            cache_repo=self.mock_cache_repo,
            cache_serializer=self.mock_cache_serializer
        )
        
        # Настраиваем поведение кэша: всегда возвращаем None (кеш пустой)
        self.mock_cache_repo.get.return_value = None
    
    def tearDown(self):
        self.patcher_logger.stop()
    
    async def test_successful_auth(self):
        """Успешная аутентификация пользователя"""
        test_username = "testuser"
        test_password = "correct_password"
        test_user_id = "123"
        
        mock_user = MagicMock()
        mock_user.id = test_user_id
        mock_user.password_hash.value = test_password
        
        self.mock_user_repo.get_by_username.return_value = mock_user
        
        result = await self.use_case.execute(
            username=test_username,
            password=test_password
        )
        
        # Исправлено: проверяем позиционный аргумент вместо именованного
        self.mock_user_repo.get_by_username.assert_awaited_once_with(test_username)
        self.mock_logger.debug.assert_any_call(f"{test_username} tries to log in")
        self.mock_logger.debug.assert_any_call("Successfully logged in")
        self.assertEqual(result, test_user_id)
        self.mock_cache_repo.set.assert_awaited_once()
    
    async def test_user_not_found(self):
        """Попытка аутентификации несуществующего пользователя"""
        test_username = "unknown"
        test_password = "any"
        
        self.mock_user_repo.get_by_username.return_value = None
        
        with pytest.raises(UserNotFoundError) as exc_info:
            await self.use_case.execute(
                username=test_username,
                password=test_password
            )
        
        assert f"User {test_username} does not exists" in str(exc_info.value)
        # Исправлено: проверяем позиционный аргумент
        self.mock_user_repo.get_by_username.assert_awaited_once_with(test_username)
        self.mock_logger.debug.assert_any_call(f"{test_username} tries to log in")
        self.mock_logger.debug.assert_any_call(f"{test_username} doesn't exists")
        self.mock_cache_repo.set.assert_not_called()
    
    async def test_invalid_password(self):
        """Попытка аутентификации с неверным паролем"""
        test_username = "testuser"
        correct_password = "valid_pass"
        wrong_password = "invalid_pass"
        
        mock_user = MagicMock()
        mock_user.password_hash.value = correct_password
        
        self.mock_user_repo.get_by_username.return_value = mock_user
        
        with pytest.raises(InvalidPasswordError) as exc_info:
            await self.use_case.execute(
                username=test_username,
                password=wrong_password
            )
        
        assert "Invalid credentials" in str(exc_info.value)
        # Исправлено: проверяем позиционный аргумент
        self.mock_user_repo.get_by_username.assert_awaited_once_with(test_username)
        self.mock_logger.debug.assert_any_call(f"{test_username} tries to log in")
        self.mock_logger.debug.assert_any_call("Invalid password")
        self.mock_cache_repo.set.assert_not_called()