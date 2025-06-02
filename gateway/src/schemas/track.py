from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ArtistResponse(BaseModel):
    artist_id: int
    name: str
    is_verified: bool = False

class GenreResponse(BaseModel):
    genre_id: int
    name: str

class TrackResponse(BaseModel):
    track_id: int
    title: str
    duration_ms: int
    artists: List[ArtistResponse]
    genres: List[GenreResponse]
    explicit: bool
    release_date: str

class TracksPaginationResponse(BaseModel):
    tracks: List[TrackResponse]
    total: int = Field(..., description="Total number of tracks")
    offset: int = Field(0, ge=0)
    limit: int = Field(50, le=100)

class TracksByArtistRequest(BaseModel):
    artist_id: int = Field(..., description="ID of the artist")
    offset: int = Field(0, ge=0)
    limit: int = Field(50, le=100)

class TracksByGenreRequest(BaseModel):
    genre_id: int = Field(..., description="ID of the genre")
    offset: int = Field(0, ge=0)
    limit: int = Field(50, le=100)



class TrackItemResponse(BaseModel):
    track_id: int
    title: str
    duration_ms: int
    artists: List[str]
    genres: List[str]
    explicit: bool
    release_date: str

class TrackSearchRequest(BaseModel):
    title: Optional[str] = None
    artist_name: Optional[str] = None
    genre_name: Optional[List[str]] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    explicit: Optional[bool] = None
    release_date_from: Optional[date] = None
    release_date_to: Optional[date] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)

class TrackSearchResponse(BaseModel):
    tracks: List[TrackItemResponse]
    total: int
    page: int
    page_size: int