# tests/unit/application/test_get_track.py
import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.applications.use_cases.get_track import GetTrackUseCase
from src.domain.music_catalog.models import Track, ArtistInfo, Genre
from src.core.exceptions import TrackNotFound
from src.domain.cache.cache_repository import CacheTTL

class TestGetTrackUseCase(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_music_repo = AsyncMock()
        self.mock_cache_repo = AsyncMock()
        self.mock_cache_serializer = MagicMock()
        
        self.use_case = GetTrackUseCase(
            music_repo=self.mock_music_repo,
            cache_repo=self.mock_cache_repo,
            cache_serializer=self.mock_cache_serializer
        )
        
        # Настраиваем поведение кэша по умолчанию: кэш пуст
        self.mock_cache_repo.get.return_value = None
        
        # Тестовые данные
        self.track_id = 1
        self.artist = ArtistInfo(artist_id=1, name="Test Artist", is_verified=True)
        self.genre = Genre(genre_id=1, name="Rock")
        self.mock_track = Track(
            track_id=self.track_id,
            title="Test Track",
            duration=300000,
            artists=[self.artist],
            genres=[self.genre],
            explicit=False
        )
    
    async def test_successful_track_fetch_from_repo(self):
        """Успешное получение трека из репозитория (кэш пуст)"""
        self.mock_music_repo.get_by_id.return_value = self.mock_track
        
        result = await self.use_case.execute(self.track_id)
        
        # Проверяем вызовы
        self.mock_cache_repo.get.assert_awaited_once()
        self.mock_music_repo.get_by_id.assert_awaited_once_with(track_id=self.track_id)
        
        # Проверяем сериализацию и сохранение в кэш
        self.mock_cache_serializer.serialize.assert_called_once_with(self.mock_track)
        self.mock_cache_repo.set.assert_awaited_once_with(
            f"GetTrackUseCase:execute:{self.track_id}:",  # Исправленный формат ключа
            self.mock_cache_serializer.serialize.return_value,
            CacheTTL.DEFAULT
        )
        
        # Проверяем результат
        self.assertEqual(result, self.mock_track)
    
    async def test_successful_track_fetch_from_cache(self):
        """Успешное получение трека из кэша"""
        # Настраиваем кэш
        self.mock_cache_repo.get.return_value = b"cached_data"
        self.mock_cache_serializer.deserialize.return_value = self.mock_track
        
        result = await self.use_case.execute(self.track_id)
        
        # Проверяем вызовы
        self.mock_cache_repo.get.assert_awaited_once()
        # Учитываем второй аргумент (тип объекта)
        self.mock_cache_serializer.deserialize.assert_called_once_with(
            b"cached_data", 
            Track
        )
        
        # Проверяем, что репозиторий не вызывался
        self.mock_music_repo.get_by_id.assert_not_called()
        
        # Проверяем, что не было попытки сохранить в кэш
        self.mock_cache_repo.set.assert_not_called()
        
        # Проверяем результат
        self.assertEqual(result, self.mock_track)
    
    async def test_track_not_found(self):
        """Обработка случая, когда трек не найден"""
        self.mock_music_repo.get_by_id.return_value = None
        
        with pytest.raises(TrackNotFound) as exc_info:
            await self.use_case.execute(self.track_id)
        
        # Проверяем сообщение об ошибке
        assert f"Track_{self.track_id} not found" in str(exc_info.value)
        
        # Проверяем вызовы
        self.mock_music_repo.get_by_id.assert_awaited_once_with(track_id=self.track_id)
        
        # Проверяем, что не было попытки сохранить в кэш
        self.mock_cache_serializer.serialize.assert_not_called()
        self.mock_cache_repo.set.assert_not_called()