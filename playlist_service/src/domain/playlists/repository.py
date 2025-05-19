from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.playlists.models import Playlist

class PlaylistRepository(ABC):
    @abstractmethod
    async def get_by_id(self, playlist_id: int) -> Optional[Playlist]:
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, playlist: Playlist) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_playlist_owner(self, playlist_id: int) -> Optional[int]:
        """Возвращает ID владельца плейлиста"""
        raise NotImplementedError
    
    @abstractmethod
    async def add_track(self, playlist_id: int, track_id: int) -> None:
        raise NotImplementedError
        
    @abstractmethod
    async def remove_track(self, playlist_id: int, track_id: int) -> bool:
        raise NotImplementedError
        
    @abstractmethod
    async def create_playlist(self, name: str, user_id: int, is_public: bool = False) -> int:
        raise NotImplementedError
        
    @abstractmethod
    async def get_user_playlists(self, user_id: int) -> List[Playlist]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_playlists_with_track(self, track_id: int) ->  List[Playlist]:
        raise NotImplementedError
    
    @abstractmethod
    async def remove_track_and_reorder(self, playlist_id: int, track_id: int) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def delete_user_playlist_relations(self, user_id: int) -> int:
        """
        Удаляет все связи пользователя с плейлистами (из playlist_users)
        Возвращает количество удаленных связей
        """
        raise NotImplementedError
