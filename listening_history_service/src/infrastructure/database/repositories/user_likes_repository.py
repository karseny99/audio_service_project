from typing import Optional, List
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings
from src.infrastructure.database.repositories.database import ConnectionDecorator
from src.domain.user_likes.repository import UserLikesRepository
from src.domain.user_likes.models import UserLike
from src.infrastructure.database.models import UserLikeORM
from src.domain.user_likes.value_objects import UserId, TrackId
from src.core.exceptions import TrackAlreadyLiked


class PostgresUserLikesRepository(UserLikesRepository):
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.get_postgres_url(),
            echo=False
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def add_like(self, user_id: UserId, track_id: TrackId, session: Optional[AsyncSession] = None) -> None:
        # Проверяем, не существует ли уже такого лайка
        existing_like = await session.get(UserLikeORM, (user_id, track_id))
        if existing_like:
            raise TrackAlreadyLiked(f"User {user_id} already liked track {track_id}")

        new_like = UserLikeORM(
            user_id=user_id,
            track_id=track_id
        )
        session.add(new_like)

    @ConnectionDecorator()
    async def remove_like(self, user_id: UserId, track_id: TrackId, session: Optional[AsyncSession] = None) -> bool:
        stmt = delete(UserLikeORM).where(
            (UserLikeORM.user_id == user_id) &
            (UserLikeORM.track_id == track_id)
        ).returning(UserLikeORM.user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_user_likes(self, user_id: UserId, session: Optional[AsyncSession] = None) -> List[UserLike]:
        stmt = select(UserLikeORM).where(
            UserLikeORM.user_id == user_id
        ).order_by(UserLikeORM.liked_at.desc())
        
        result = await session.execute(stmt)
        return [like.to_domain() for like in result.scalars()]

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def is_liked(self, user_id: UserId, track_id: TrackId, session: Optional[AsyncSession] = None) -> bool:
        stmt = select(UserLikeORM).where(
            (UserLikeORM.user_id == user_id) &
            (UserLikeORM.track_id == track_id)
        ).limit(1)
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    