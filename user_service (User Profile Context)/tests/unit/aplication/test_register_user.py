import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.register_user import (
    RegisterUserUseCase,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError
)
from src.domain.users.models import User
from src.domain.users.value_objects.email import EmailAddress
from src.domain.users.value_objects.password_hash import PasswordHash
from src.domain.users.value_objects.username import Username
from src.core.logger import logger

class TestRegisterUserUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_user_repo = AsyncMock()
        self.mock_event_publisher = AsyncMock()
        self.mock_registration_service = MagicMock()
        self.mock_logger = MagicMock()

        # ВАЖНО: патчим logger по месту его использования
        self.patcher_logger = patch("src.applications.use_cases.register_user.logger", self.mock_logger)
        self.patcher_logger.start()

        self.use_case = RegisterUserUseCase(
            user_repo=self.mock_user_repo,
            event_publisher=self.mock_event_publisher,
            registration_service=self.mock_registration_service
        )

    
    def tearDown(self):
        self.patcher_logger.stop()
    
    async def test_successful_registration(self):
        """Test successful user registration flow"""
        test_email = "test@example.com"
        test_password = "password123"
        test_username = "testuser"
        
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.get_by_username.return_value = None
        
        mock_user = User(
            id=1,
            email=EmailAddress(test_email),
            username=Username(test_username),
            password_hash=PasswordHash(test_password)
        )
        self.mock_registration_service.register_user.return_value = mock_user
        self.mock_user_repo.add.return_value = mock_user
        
        result = await self.use_case.execute(
            email=test_email,
            password=test_password,
            username=test_username
        )
        

        self.mock_user_repo.get_by_email.assert_awaited_once_with(email=test_email)

        self.mock_user_repo.get_by_username.assert_awaited_once_with(username=test_username)
        
        self.mock_registration_service.register_user.assert_called_once_with(
            email=test_email,
            username=test_username,
            password=test_password
        )
        
        self.mock_user_repo.add.assert_awaited_once_with(user=mock_user)
        
        self.mock_logger.info.assert_called_once_with(f"Registered: {mock_user}")
        
        self.assertEqual(result, "1")
    
    async def test_email_already_exists(self):
        """Test registration with existing email"""
        # Arrange
        test_email = "john@mail.com"
        test_password = "password123"
        test_username = "newuser"
        
        # Mock existing email
        self.mock_user_repo.get_by_email.return_value = MagicMock()
        
        # Act/Assert
        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            await self.use_case.execute(
                email=test_email,
                password=test_password,
                username=test_username
            )
        
        # Проверка сообщения об ошибке
        assert "Email exists" in str(exc_info.value)
        
        # Проверка логгирования - должно быть сообщение с EMAIL
        self.mock_logger.debug.assert_called_once_with(f"{test_email} exists")
        
        # Проверка что не было попытки создать пользователя
        self.mock_registration_service.register_user.assert_not_called()
        self.mock_user_repo.add.assert_not_called()
    
    async def test_username_already_exists(self):
        """Test registration with existing username"""
        # Arrange
        test_email = "new@example.com"
        test_password = "password123"
        test_username = "johndoe"
        
        # Mock responses
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.get_by_username.return_value = MagicMock()
        
        # Act/Assert
        with pytest.raises(UsernameAlreadyExistsError) as exc_info:
            await self.use_case.execute(
                email=test_email,
                password=test_password,
                username=test_username
            )
        
        # Проверка сообщения об ошибке
        assert "Username exists" in str(exc_info.value)
        
        # Проверка логгирования - должно быть сообщение с USERNAME
        self.mock_logger.debug.assert_called_once_with(f"{test_username} exists")
        
        # Проверка что не было попытки создать пользователя
        self.mock_registration_service.register_user.assert_not_called()
        self.mock_user_repo.add.assert_not_called()
    
    async def test_user_creation_failure(self):
        """Test error during user creation"""
        
        test_email = "test@example.com"
        test_password = "password123"
        test_username = "test_user"
        
        
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.get_by_username.return_value = None
        
        
        error_message = "Invalid email format"
        self.mock_registration_service.register_user.side_effect = ValueError(error_message)
        
        
        with pytest.raises(ValueError) as exc_info:
            await self.use_case.execute(
                email=test_email,
                password=test_password,
                username=test_username
            )
        
        
        assert error_message in str(exc_info.value)
        
        
        self.mock_user_repo.add.assert_not_called()