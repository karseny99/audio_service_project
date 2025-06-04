from typing import Optional, List
from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings
from src.infrastructure.database.repositories.database import ConnectionDecorator
from src.domain.playlists.repository import PlaylistRepository
from src.domain.playlists.models import Playlist, PlaylistTrack
from src.infrastructure.database.models import (
    PlaylistORM, 
    PlaylistUserORM, 
    PlaylistTrackORM
)

class PostgresPlaylistRepository(PlaylistRepository):
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
    async def get_by_id(self, playlist_id: int, session: Optional[AsyncSession] = None) -> Optional[Playlist]:
        playlist_orm = await session.get(PlaylistORM, playlist_id)
        if not playlist_orm:
            return None
        
        # Явная загрузка связанных данных
        await session.refresh(playlist_orm, ['tracks', 'users'])
        return playlist_orm.to_domain()

    @ConnectionDecorator()
    async def update(self, playlist: Playlist, session: Optional[AsyncSession] = None) -> None:
        playlist_orm = await session.get(PlaylistORM, playlist.playlist_id)
        if playlist_orm:
            playlist_orm.name = playlist.name
            playlist_orm.is_public = playlist.is_public
            await session.flush()

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_playlist_owner(self, playlist_id: int, session: Optional[AsyncSession] = None) -> Optional[int]:
        stmt = select(PlaylistUserORM.user_id).where(
            (PlaylistUserORM.playlist_id == playlist_id) &
            (PlaylistUserORM.is_creator == True)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @ConnectionDecorator()
    async def add_track(self, playlist_id: int, track_id: int, session: Optional[AsyncSession] = None) -> None:
        from src.domain.playlists.models import TrackId
        
        # Проверка через VO
        try:
            TrackId(track_id)  # Валидация ID трека
        except ValueError as e:
            raise ValueError(f"Invalid track ID: {str(e)}")
        
        # Остальная логика добавления...
        max_pos = await session.scalar(
            select(func.max(PlaylistTrackORM.position))
            .where(PlaylistTrackORM.playlist_id == playlist_id)
        ) or 0
        
        new_track = PlaylistTrackORM(
            playlist_id=playlist_id,
            track_id=track_id,
            position=max_pos + 1
        )
        session.add(new_track)

    @ConnectionDecorator()
    async def remove_track(self, playlist_id: int, track_id: int, session: Optional[AsyncSession] = None) -> bool:
        stmt = delete(PlaylistTrackORM).where(
            (PlaylistTrackORM.playlist_id == playlist_id) &
            (PlaylistTrackORM.track_id == track_id)
        ).returning(PlaylistTrackORM.playlist_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @ConnectionDecorator()
    async def create_playlist(self, name: str, user_id: int, is_public: bool = False, 
                            session: Optional[AsyncSession] = None) -> int:
        playlist_orm = PlaylistORM(
            name=name,
            is_public=is_public
        )
        session.add(playlist_orm)
        await session.flush()
        
        # Добавляем владельца
        session.add(PlaylistUserORM(
            playlist_id=playlist_orm.playlist_id,
            user_id=user_id,
            is_creator=True
        ))
        
        return playlist_orm.playlist_id

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_user_playlists(self, user_id: int, session: Optional[AsyncSession] = None) -> List[Playlist]:
        stmt = (
            select(PlaylistORM)
            .join(PlaylistUserORM)
            .where(PlaylistUserORM.user_id == user_id)
            .options(
                joinedload(PlaylistORM.tracks),
                joinedload(PlaylistORM.users)
            )
        )
    
        result = await session.execute(stmt)
        return [playlist.to_domain() for playlist in result.unique().scalars()]
    
    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_playlist_tracks(self, playlist_id: int, session: Optional[AsyncSession] = None) -> List[PlaylistTrack]:
        stmt = select(PlaylistTrackORM).where(
            PlaylistTrackORM.playlist_id == playlist_id
        ).order_by(PlaylistTrackORM.position)
        
        result = await session.execute(stmt)
        return [track.to_domain() for track in result.scalars()]

    @ConnectionDecorator()
    async def delete_playlist(self, playlist_id: int, session: Optional[AsyncSession] = None) -> bool:
        stmt = delete(PlaylistORM).where(
            PlaylistORM.playlist_id == playlist_id
        ).returning(PlaylistORM.playlist_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def get_playlists_with_track(self, track_id: int, session: Optional[AsyncSession] = None) -> List[Playlist]:
        stmt = select(PlaylistORM).join(
            PlaylistTrackORM,
            PlaylistTrackORM.playlist_id == PlaylistORM.playlist_id
        ).where(PlaylistTrackORM.track_id == track_id)
        
        result = await session.execute(stmt)
        playlists = [playlist.to_domain() for playlist in result.scalars()]
        
        # Дополнительная загрузка данных
        for playlist in playlists:
            await session.refresh(playlist, ['tracks', 'users'])
            
        return playlists

    @ConnectionDecorator()
    async def remove_track_and_reorder(self, playlist_id: int, track_id: int, session: Optional[AsyncSession] = None) -> None:
        # 1. Удаляем трек
        stmt = delete(PlaylistTrackORM).where(
            (PlaylistTrackORM.playlist_id == playlist_id) &
            (PlaylistTrackORM.track_id == track_id)
        )
        await session.execute(stmt)
        
        # 2. Получаем оставшиеся треки
        stmt = select(PlaylistTrackORM).where(
            PlaylistTrackORM.playlist_id == playlist_id
        ).order_by(PlaylistTrackORM.position)
        result = await session.execute(stmt)
        tracks = result.scalars().all()
        
        # 3. Пересчитываем позиции
        for index, track in enumerate(tracks):
            track.position = index
        
        await session.flush()

    @ConnectionDecorator()
    async def delete_user_playlist_relations(self, user_id: int, session: Optional[AsyncSession] = None) -> int:
        """
        Удаляет все записи пользователя из таблицы playlist_users
        Возвращает количество удаленных связей
        """
        delete_stmt = delete(PlaylistUserORM).where(
            PlaylistUserORM.user_id == user_id
        ).returning(PlaylistUserORM.playlist_id)
        
        result = await session.execute(delete_stmt)
        deleted_records = result.all()
        
        return len(deleted_records)
    
    @ConnectionDecorator(isolation_level="READ COMMITTED")
    async def is_public(self, playlist_id: int, session: Optional[AsyncSession] = None) -> bool:
        stmt = select(PlaylistORM.is_public).where(
            PlaylistORM.playlist_id == playlist_id
        )
        result = await session.execute(stmt)
        return result.scalar_one()
