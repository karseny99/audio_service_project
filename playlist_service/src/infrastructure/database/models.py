from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, ForeignKey, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from src.domain.playlists.models import Playlist as DomainPlaylist
from src.domain.playlists.models import PlaylistTrack
from src.domain.playlists.models import (
    Playlist,
    PlaylistTitle,
    UserId,
    TrackId,
    PlaylistTrack
)

class Base(DeclarativeBase):
    pass

class PlaylistORM(Base):
    __tablename__ = 'playlists'
    __table_args__ = {'schema': 'playlist'}
    
    playlist_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Явно указываем схему в relationship
    tracks: Mapped[List["PlaylistTrackORM"]] = relationship(
        "PlaylistTrackORM",
        back_populates="playlist",
        cascade="all, delete-orphan"
    )
    
    users: Mapped[List["PlaylistUserORM"]] = relationship(
        "PlaylistUserORM",
        back_populates="playlist",
        cascade="all, delete-orphan"
    )


    def to_domain(self) -> Playlist:
        """Преобразование ORM -> Domain модель с Value Objects"""
        owner = next((u.user_id for u in self.users if u.is_creator), None)
        
        return Playlist(
            playlist_id=self.playlist_id,
            name=PlaylistTitle(self.name),
            owner_id=UserId(owner) if owner else None,
            is_public=self.is_public,
            created_at=self.created_at,
            tracks=[
                PlaylistTrack(
                    track_id=TrackId(t.track_id),
                    position=t.position,
                    added_at=t.added_at
                ) for t in sorted(self.tracks, key=lambda x: x.position)
            ]
        )



class PlaylistTrackORM(Base):
    __tablename__ = 'playlist_tracks'
    __table_args__ = {'schema': 'playlist'}
    
    playlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('playlist.playlists.playlist_id', ondelete="CASCADE"),
        primary_key=True
    )

    track_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    playlist: Mapped["PlaylistORM"] = relationship(
        "PlaylistORM",
        back_populates="tracks"
    )

    def to_domain(self) -> PlaylistTrack:
        """Преобразование ORM -> Domain модель трека"""
        return PlaylistTrack(
            track_id=TrackId(self.track_id),
            position=self.position,
            added_at=self.added_at
        )



class PlaylistUserORM(Base):
    __tablename__ = 'playlist_users'
    __table_args__ = {'schema': 'playlist'}
    
    playlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('playlist.playlists.playlist_id', ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_creator: Mapped[bool] = mapped_column(Boolean, default=False)
    
    playlist: Mapped["PlaylistORM"] = relationship(
        "PlaylistORM",
        back_populates="users"
    )