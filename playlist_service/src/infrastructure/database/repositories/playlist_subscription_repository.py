from typing import Optional, List
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models import PlaylistUserORM
from src.domain.playlists.repository import PlaylistSubscriptionRepository
from src.infrastructure.database.repositories.database import ConnectionDecorator

class PostgresPlaylistSubscriptionRepository(PlaylistSubscriptionRepository):
    @ConnectionDecorator()
    async def is_subscribed(self, user_id: str, playlist_id: int, session: Optional[AsyncSession] = None) -> bool:
        stmt = select(PlaylistUserORM).where(
            (PlaylistUserORM.user_id == int(user_id)) &
            (PlaylistUserORM.playlist_id == playlist_id) &
            (PlaylistUserORM.is_creator == False)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @ConnectionDecorator()
    async def add_subscription(self, user_id: str, playlist_id: int, session: Optional[AsyncSession] = None) -> None:
        # Проверка на дубликат
        if not await self.is_subscribed(user_id, playlist_id):
            new_sub = PlaylistUserORM(
                playlist_id=playlist_id,
                user_id=int(user_id),
                is_creator=False
            )
            session.add(new_sub)