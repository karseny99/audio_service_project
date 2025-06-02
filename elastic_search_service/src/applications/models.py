from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ElasticTrackRequest(BaseModel):
    """
    Все поля опциональны - если пользователь ничего не передал, вернём ошибку.
    """
    title: Optional[str] = Field(None, description="Часть названия трека для поиска")
    artist_name: Optional[str] = Field(None, description="Имя артиста (или фрагмент) для поиска")
    genre_name: Optional[List[str]] = Field(
        None,
        description="Список жанров (если хотим искать по нескольким)"
    )
    min_duration_ms: Optional[int] = Field(None, description="Минимальная длительность (ms)")
    max_duration_ms: Optional[int] = Field(None, description="Максимальная длительность (ms)")
    explicit: Optional[bool] = Field(None, description="Флаг explicit")
    release_date_from: Optional[date] = Field(None, description="Дата релиза от")
    release_date_to: Optional[date] = Field(None, description="Дата релиза до")

    # Пагинация:
    page: Optional[int] = Field(1, ge=1, description="Номер страницы (>= 1)")
    page_size: Optional[int] = Field(50, ge=1, le=100, description="Кол-во элементов на странице (максимум 100)")


class TrackItem(BaseModel):
    """
    Единичный трек в ответе (поля соответствуют тому, что хранится в Elasticsearch).
    """
    track_id: Optional[int]
    title: Optional[str]
    duration_ms: Optional[int]
    artists: Optional[List[str]]            # здесь просто имена артистов
    genres: Optional[List[str]]             # имена жанров
    explicit: Optional[bool]
    release_date: Optional[date]


class ElasticTrackResponse(BaseModel):
    """
    Обёртка-ответ для поиска треков.
    """
    tracks: List[TrackItem]
    total: int                              # общее число найденных документов
    page: int
    page_size: int
    success: bool