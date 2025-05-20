from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.user_likes.models import UserLike

class UserLikesRepository(ABC):
    @abstractmethod
    async def add_like(self, user_id: int, track_id: int) -> None:
        """Добавляет лайк треку от пользователя."""
        raise NotImplementedError
    
    @abstractmethod
    async def remove_like(self, user_id: int, track_id: int) -> bool:
        """Удаляет лайк треку от пользователя, возвращает успешность операции"""
        raise NotImplementedError
        
    @abstractmethod
    async def get_user_likes(self, user_id: int) -> List[int]:
        """Возвращает список ID треков, которые лайкнул пользователь"""
        raise NotImplementedError
        
    @abstractmethod
    async def is_liked(self, user_id: int, track_id: int) -> bool:
        """Проверяет, лайкнул ли пользователь трек"""
        raise NotImplementedError