from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class ArtistResponse(BaseModel):
    artist_id: int
    name: str
    is_verified: bool = False

class GenreResponse(BaseModel):
    genre_id: int
    name: str


class ArtistResponse(BaseModel):
    artist_id: int
    name: str
    is_verified: bool

class GenreResponse(BaseModel):
    genre_id: int
    name: str

class TrackResponse(BaseModel):
    track_id: int
    title: str
    artists: List[ArtistResponse]
    genres: List[GenreResponse]
    duration_ms: int
    explicit: bool
    release_date: str  # ISO format date string
    created_at: datetime

class PaginationResponse(BaseModel):
    offset: int
    limit: int
    total: int

class TracksPaginationResponse(BaseModel):
    tracks: List[TrackResponse]
    pagination: PaginationResponse

    @classmethod
    def from_proto(cls, proto_response):
        """Alternative constructor from protobuf message"""
        return cls(
            tracks=[TrackResponse(
                track_id=t.track_id,
                title=t.title,
                artists=[ArtistResponse(
                    artist_id=a.artist_id,
                    name=a.name,
                    is_verified=a.is_verified
                ) for a in t.artists],
                genres=[GenreResponse(
                    genre_id=g.genre_id,
                    name=g.name
                ) for g in t.genres],
                duration_ms=t.duration_ms,
                explicit=t.explicit,
                release_date=t.release_date,
                created_at=t.created_at.ToDatetime()
            ) for t in proto_response.tracks],
            pagination=PaginationResponse(
                offset=proto_response.pagination.offset,
                limit=proto_response.pagination.limit,
                total=proto_response.pagination.total
            )
        )

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