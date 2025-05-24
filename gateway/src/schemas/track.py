from pydantic import BaseModel, Field
from typing import List

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