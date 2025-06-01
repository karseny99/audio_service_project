import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.change_password import ChangePasswordUseCase
from src.core.exceptions import UserNotFoundError, InvalidPasswordError

class TestChangePasswordUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_user_repo = AsyncMock()
        self.mock_event_publisher = AsyncMock()
        
        self.use_case = ChangePasswordUseCase(
            user_repo=self.mock_user_repo,
            event_publisher=self.mock_event_publisher
        )
    
    async def test_successful_password_change(self):
        """Успешная смена пароля"""
        user_id = 3
        old_password = "string"
        new_password = "string"
        
        # Создаем мок пользователя с правильным старым паролем
        mock_user = MagicMock()
        mock_user.password_hash.value = old_password
        
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        # Выполняем use case
        await self.use_case.execute(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password
        )
        
        # Проверяем вызовы
        self.mock_user_repo.get_by_id.assert_awaited_once_with(user_id)
        mock_user.change_password.assert_called_once()
        self.mock_user_repo.update.assert_awaited_once_with(mock_user)
    
    async def test_user_not_found(self):
        """Попытка смены пароля для несуществующего пользователя"""
        user_id = 999
        self.mock_user_repo.get_by_id.return_value = None
        
        with pytest.raises(UserNotFoundError) as exc_info:
            await self.use_case.execute(
                user_id=user_id,
                old_password="any",
                new_password="new"
            )
        
        assert f"User {user_id} not found" in str(exc_info.value)
        self.mock_user_repo.get_by_id.assert_awaited_once_with(user_id)
        self.mock_user_repo.update.assert_not_called()
    
    async def test_invalid_old_password(self):
        """Попытка смены пароля с неверным старым паролем"""
        user_id = 3
        real_old_password = "string"
        wrong_old_password = "wrong_old_pass"
        new_password = "new_pass"
        
        # Создаем мок пользователя с реальным паролем
        mock_user = MagicMock()
        mock_user.password_hash.value = real_old_password
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        with pytest.raises(InvalidPasswordError) as exc_info:
            await self.use_case.execute(
                user_id=user_id,
                old_password=wrong_old_password,
                new_password=new_password
            )
        
        assert "Old password incorrect" in str(exc_info.value)
        self.mock_user_repo.get_by_id.assert_awaited_once_with(user_id)
        mock_user.change_password.assert_not_called()
        self.mock_user_repo.update.assert_not_called()
    
    async def test_password_change_verification(self):
        """Проверка корректности генерации нового хеша пароля"""
        user_id = 3
        old_password = "string"
        new_password = "new_secure"
        
        mock_user = MagicMock()
        mock_user.password_hash.value = old_password
        self.mock_user_repo.get_by_id.return_value = mock_user
        
        await self.use_case.execute(user_id, old_password, new_password)
        
        # Проверяем что change_password вызван с объектом PasswordHash
        args, _ = mock_user.change_password.call_args
        new_password_hash = args[0]
        
        # Проверяем тип и значение нового хеша
        from src.domain.users.value_objects.password_hash import PasswordHash
        assert isinstance(new_password_hash, PasswordHash)
        assert new_password_hash.value == new_password

if __name__ == "__main__":
    unittest.main()