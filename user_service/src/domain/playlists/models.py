# src/domain/playlists/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List
from src.domain.events.events import PlaylistCreated, TrackAddedToPlaylist
from src.domain.exceptions import DomainException

@dataclass
class TrackPosition:
    track_id: int
    position: int

class Playlist:
    def __init__(
        self,
        playlist_id: int,
        name: str,
        owner_id: int,
        is_favourite: bool = False,
        tracks: List[TrackPosition] = None,
        created_at: datetime = None
    ):
        self._id = playlist_id
        self._name = name
        self._owner_id = owner_id
        self._is_favourite = is_favourite
        self._tracks = tracks or []
        self._created_at = created_at or datetime.utcnow()
        self._version = 0  # Для оптимистичной блокировки
        self._events = []  # Список доменных событий

        # Валидация при создании
        if not name:
            raise DomainException("Playlist name cannot be empty")
        
        # Генерируем событие создания
        self._add_event(
            PlaylistCreated(
                playlist_id=self._id,
                owner_id=self._owner_id,
                name=self._name,
                occurred_on=self._created_at
            )
        )

    def add_track(self, track_id: int, position: int = None) -> None:
        """Добавляет трек в плейлист с проверкой инвариантов"""
        if any(t.track_id == track_id for t in self._tracks):
            raise DomainException("Track already exists in playlist")

        new_position = position if position is not None else len(self._tracks) + 1
        self._tracks.append(TrackPosition(track_id=track_id, position=new_position))
        
        # Нормализация позиций
        self._normalize_positions()
        
        self._add_event(
            TrackAddedToPlaylist(
                playlist_id=self._id,
                track_id=track_id,
                position=new_position,
                occurred_on=datetime.utcnow()
            )
        )
        self._version += 1

    def _normalize_positions(self) -> None:
        """Упорядочивает позиции треков (1, 2, 3...)"""
        sorted_tracks = sorted(self._tracks, key=lambda x: x.position)
        for idx, track in enumerate(sorted_tracks, start=1):
            track.position = idx

    def _add_event(self, event) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()

    # Properties (доступ только для чтения)
    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def owner_id(self) -> int:
        return self._owner_id

    @property
    def tracks(self) -> List[TrackPosition]:
        return self._tracks.copy()  # Возвращаем копию для иммутабельности

    @property
    def version(self) -> int:
        return self._version

    @property
    def events(self) -> list:
        return self._events.copy()