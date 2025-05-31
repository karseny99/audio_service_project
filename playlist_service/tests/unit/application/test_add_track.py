import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.add_track import AddTrackToPlaylistUseCase
from src.core.exceptions import TrackNotFoundError, InsufficientPermission
from src.domain.playlists.models import TrackAlreadyInPlaylist

class TestAddTrackToPlaylistUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_playlist_repo = AsyncMock()
        self.mock_track_service = AsyncMock()
        self.mock_event_publisher = AsyncMock()
        
        self.use_case = AddTrackToPlaylistUseCase(
            playlist_repo=self.mock_playlist_repo,
            track_service=self.mock_track_service,
            event_publisher=self.mock_event_publisher
        )
        
        # Общие тестовые данные
        self.playlist_id = "playlist_1"
        self.track_id = "track_99"
        self.owner_id = "user_42"
        self.non_owner_id = "user_99"
        
        # Мок владельца плейлиста
        self.mock_owner = MagicMock()
        self.mock_owner.id = self.owner_id

    async def test_track_not_found(self):
        """Проверка ошибки при отсутствии трека"""
        self.mock_track_service.verify_track_exists.return_value = False
        
        with pytest.raises(TrackNotFoundError) as exc_info:
            await self.use_case.execute(
                playlist_id=self.playlist_id,
                track_id=self.track_id,
                user_id=self.owner_id
            )
        
        assert f"Track {self.track_id} not found" in str(exc_info.value)
        self.mock_track_service.verify_track_exists.assert_awaited_once_with(self.track_id)

    async def test_user_not_owner(self):
        """Проверка прав доступа"""
        self.mock_track_service.verify_track_exists.return_value = True
        self.mock_playlist_repo.get_playlist_owner.return_value = self.mock_owner
        
        with pytest.raises(InsufficientPermission) as exc_info:
            await self.use_case.execute(
                playlist_id=self.playlist_id,
                track_id=self.track_id,
                user_id=self.non_owner_id
            )
        
        assert f"User {self.non_owner_id} does not have such rights" in str(exc_info.value)
        self.mock_playlist_repo.get_playlist_owner.assert_awaited_once_with(self.playlist_id)

    async def test_successful_add_track(self):
        """Успешное добавление трека"""
        self.mock_track_service.verify_track_exists.return_value = True
        self.mock_playlist_repo.get_playlist_owner.return_value = self.mock_owner
        
        # Мок плейлиста с методом add_track
        mock_playlist = MagicMock()
        self.mock_playlist_repo.get_by_id.return_value = mock_playlist
        
        await self.use_case.execute(
            playlist_id=self.playlist_id,
            track_id=self.track_id,
            user_id=self.owner_id
        )
        
        # Проверка вызовов
        mock_playlist.add_track.assert_called_once_with(self.track_id)
        self.mock_playlist_repo.update.assert_awaited_once_with(mock_playlist)

    async def test_duplicate_track(self):
        """Проверка добавления дубликата трека"""
        self.mock_track_service.verify_track_exists.return_value = True
        self.mock_playlist_repo.get_playlist_owner.return_value = self.mock_owner
        
        mock_playlist = MagicMock()
        self.mock_playlist_repo.get_by_id.return_value = mock_playlist
        mock_playlist.add_track.side_effect = TrackAlreadyInPlaylist("Трек уже в плейлисте")
        
        with pytest.raises(TrackAlreadyInPlaylist):
            await self.use_case.execute(
                playlist_id=self.playlist_id,
                track_id=self.track_id,
                user_id=self.owner_id
            )
        
        # Проверка что update не вызывался после ошибки
        self.mock_playlist_repo.update.assert_not_called()