from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from sqlalchemy.dialects.postgresql import TIMESTAMP as PostgresTIMESTAMP

from src.domain.user_likes.models import UserLike as DomainUserLike
from src.domain.user_likes.models import UserHistory as DomainUserHistory
from src.domain.user_likes.value_objects import TrackId, UserId

class Base(DeclarativeBase):
    pass

class UserLikeORM(Base):
    __tablename__ = 'user_likes'
    __table_args__ = {'schema': 'listening_history'}
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    track_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    liked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    def to_domain(self) -> DomainUserLike:
        """Convert ORM model to domain UserLike"""
        return DomainUserLike(
            user_id=UserId(self.user_id),
            track_id=TrackId(self.track_id),
            liked_at=self.liked_at
        )
    
class UserHistoryORM(Base):
    __tablename__ = 'user_history'
    __table_args__ = {'schema': 'listening_history'}
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    track_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        PostgresTIMESTAMP(timezone=True), 
        server_default=func.now(),
        nullable=True
    )
    
    def to_domain(self) -> 'DomainUserHistory':
        """Convert ORM model to domain UserHistory"""
        return DomainUserHistory(
            user_id=self.user_id,
            track_id=self.track_id,
            timestamp=self.timestamp
        )