from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from .models import User

class UserRepository(ABC):
    """Abstract interface for users logic"""
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
            Find user by id, None if not exists
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
            Find user by email, None if not exists
        """
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, user: User) -> None:
        """
            Add new user
        """
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, user: User) -> None:
        """
            Update user
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
            Delete user by user_id, 
            true if successfully deleted
            false otherwise
        """
        raise NotImplementedError
