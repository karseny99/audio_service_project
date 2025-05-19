from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date

class Base(DeclarativeBase):
    pass

class TrackORM(Base):
    __tablename__ = 'tracks'
    __table_args__ = {'schema': 'music_catalog'}

    track_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    explicit: Mapped[bool] = mapped_column(Boolean, default=False)
    release_date: Mapped[date | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default='now()')

    artists: Mapped[list['TrackArtistORM']] = relationship(back_populates='track')
    genres: Mapped[list['TrackGenreORM']] = relationship(back_populates='track')

    def to_domain(self) -> 'Track':
        from src.domain.music_catalog.models import Track, ArtistInfo, Genre
        return Track(
            track_id=self.track_id,
            title=self.title,
            duration=self.duration_ms,
            artists=[
                ArtistInfo(
                    artist_id=ta.artist.artist_id,
                    name=ta.artist.name,
                    is_verified=ta.artist.verified
                ) for ta in self.artists
            ],
            genres=[
                Genre(
                    genre_id=tg.genre.genre_id,
                    name=tg.genre.name
                ) for tg in self.genres
            ],
            explicit=self.explicit,
            release_date=self.release_date,
            created_at=self.created_at
        )

    @classmethod
    def from_domain(cls, track: 'Track') -> 'TrackORM':
        return cls(
            track_id=track.track_id,
            title=track.title,
            duration_ms=track.duration.value,
            explicit=track.explicit,
            release_date=track.release_date,
        )


class ArtistORM(Base):
    __tablename__ = 'artists'
    __table_args__ = {'schema': 'music_catalog'}

    artist_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default='now()')

class GenreORM(Base):
    __tablename__ = 'genres'
    __table_args__ = {'schema': 'music_catalog'}

    genre_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

class TrackArtistORM(Base):
    __tablename__ = 'track_artists'
    __table_args__ = {'schema': 'music_catalog'}

    track_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('music_catalog.tracks.track_id'), primary_key=True)
    artist_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('music_catalog.artists.artist_id'), primary_key=True)

    track: Mapped['TrackORM'] = relationship(back_populates='artists')
    artist: Mapped['ArtistORM'] = relationship()

class TrackGenreORM(Base):
    __tablename__ = 'track_genres'
    __table_args__ = {'schema': 'music_catalog'}

    track_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('music_catalog.tracks.track_id'), primary_key=True)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey('music_catalog.genres.genre_id'), primary_key=True)

    track: Mapped['TrackORM'] = relationship(back_populates='genres')
    genre: Mapped['GenreORM'] = relationship()