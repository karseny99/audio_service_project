from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List

class Base(DeclarativeBase):
    pass

from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Integer, DateTime
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


Base = declarative_base()

class PlaylistORM(Base):
    __tablename__ = 'playlists'
    __schema__ = 'playlist'
    
    playlist_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tracks = relationship("PlaylistTrackORM", back_populates="playlist")
    users = relationship("PlaylistUserORM", back_populates="playlist")
    
    def to_domain(self) -> DomainPlaylist:
        """Преобразование ORM -> Domain"""
        return DomainPlaylist(
            playlist_id=self.playlist_id,
            name=self.name,
            is_public=self.is_public,
            created_at=self.created_at,
            owner_id=next((u.user_id for u in self.users if u.is_creator), None),
            tracks=[t.track_id for t in self.tracks]
        )
    
    @classmethod
    def to_domain(self) -> 'Playlist':
        """Преобразование с созданием Value Objects"""
        return Playlist(
            playlist_id=self.playlist_id,
            name=PlaylistTitle(self.name),  # Создание VO
            owner_id=UserId(next((u.user_id for u in self.users if u.is_creator), None)),
            is_public=self.is_public,
            created_at=self.created_at,
            tracks=[
                PlaylistTrack(
                    track_id=TrackId(t.track_id),  # Создание VO для track_id
                    position=t.position,
                    added_at=t.added_at
                ) for t in sorted(self.tracks, key=lambda x: x.position)
            ]
        )

class PlaylistTrackORM(Base):
    __tablename__ = 'playlist_tracks'
    __schema__ = 'playlist'
    
    playlist_id = Column(BigInteger, ForeignKey('playlist.playlists.playlist_id', ondelete="CASCADE"), primary_key=True)
    track_id = Column(BigInteger, primary_key=True)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    playlist = relationship("PlaylistORM", back_populates="tracks")
    
    def to_domain(self) -> 'PlaylistTrack':
        from src.domain.playlists.models import PlaylistTrack, TrackId
        return PlaylistTrack(
            track_id=TrackId(self.track_id),  # Создание VO
            position=self.position,
            added_at=self.added_at
        )

class PlaylistUserORM(Base):
    __tablename__ = 'playlist_users'
    __schema__ = 'playlist'
    
    playlist_id = Column(BigInteger, ForeignKey('playlist.playlists.playlist_id', ondelete="CASCADE"), primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    is_creator = Column(Boolean, default=False)
    
    playlist = relationship("PlaylistORM", back_populates="users")

