from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User

class UserRepository(ABC):
    """Abstract interface for users logic"""
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
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
    async def get_by_username(self, username: str) -> Optional[User]:
        """
            Find user by email, None if not exists
        """
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, user: User) -> Optional[User]:
        """
            Add new user
        """
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, user: User) -> Optional[User]:
        """
            Update user
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
            Delete user by user_id, 
            true if successfully deleted
            false otherwise
        """
        raise NotImplementedError
