from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List

from src.domain.music_catalog.value_objects import TrackId, ArtistId, GenreId, DurationMs

@dataclass(frozen=True)
class ArtistInfo:
    artist_id: ArtistId
    name: str
    is_verified: bool = False

@dataclass(frozen=True)
class Genre:
    genre_id: GenreId
    name: str

@dataclass
class Track:
    track_id: TrackId
    title: str
    duration: DurationMs
    artists: List[ArtistInfo] = field(default_factory=list)
    genres: List[Genre] = field(default_factory=list)
    explicit: bool = False
    release_date: date = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_artist(self, artist: ArtistInfo) -> None:
        if artist not in self.artists:
            self.artists.append(artist)

    def remove_artist(self, artist_id: ArtistId) -> None:
        self.artists = [a for a in self.artists if a.artist_id != artist_id]

    def add_genre(self, genre: Genre) -> None:
        if genre not in self.genres:
            self.genres.append(genre)

    def update_metadata(self, title: str = None, duration: DurationMs = None) -> None:
        if title:
            self.title = title
        if duration:
            self.duration = duration