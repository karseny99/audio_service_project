from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.logger import logger
from src.domain.music_catalog.models import Track, Genre, ArtistInfo, DurationMs
from src.domain.music_catalog.repository import MusicRepository

from src.infrastructure.database.models import TrackORM, TrackArtistORM, TrackGenreORM
from src.infrastructure.database.repositories.database import ConnectionDecorator


class PostgresMusicRepository(MusicRepository):
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.get_postgres_url(),
            echo=False
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

    @ConnectionDecorator()
    async def get_by_id(
        self,
        track_id: int,
        session: AsyncSession | None = None
    ) -> Track | None:
        stmt = (
            select(TrackORM)
            .options(
                selectinload(TrackORM.artists).selectinload(TrackArtistORM.artist),
                selectinload(TrackORM.genres).selectinload(TrackGenreORM.genre)
            )
            .where(TrackORM.track_id == track_id)
        )
        result = await session.execute(stmt)
        track_orm = result.scalars().first()
        return self._convert_to_domain(track_orm) if track_orm else None


    @ConnectionDecorator()
    async def get_by_artist(
        self,
        artist_id: int,
        offset: int = 0,
        limit: int = 50,
        session: AsyncSession | None = None
    ) -> list[Track]:
        stmt = (
             select(TrackORM)
             .join(TrackORM.artists)
             .options(
                 selectinload(TrackORM.artists).selectinload(TrackArtistORM.artist),
                 selectinload(TrackORM.genres).selectinload(TrackGenreORM.genre)
             )
            .where(TrackArtistORM.artist_id == artist_id)
            .offset(offset)
            .limit(limit)
         )
        result = await session.execute(stmt)
        return [self._convert_to_domain(track) for track in result.scalars()]

    @ConnectionDecorator()
    async def get_by_genre(self, genre_id: int, offset: int = 0, limit: int = 50, session: AsyncSession | None = None) -> list[Track]:
        stmt = (
            select(TrackORM)
            .join(TrackORM.genres)
            .options(
                selectinload(TrackORM.artists).selectinload(TrackArtistORM.artist),
                selectinload(TrackORM.genres).selectinload(TrackGenreORM.genre)
            )
            .where(TrackGenreORM.genre_id == genre_id)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [self._convert_to_domain(track) for track in result.scalars()]


    @ConnectionDecorator()
    async def add(self, track: Track, session: AsyncSession | None = None) -> Track:
        track_orm = TrackORM(
            track_id=track.track_id,
            title=track.title,
            duration_ms=track.duration.value,
            explicit=track.explicit,
            release_date=track.release_date,
        )
        
        # Добавляем артистов
        for artist in track.artists:
            track_orm.artists.append(
                TrackArtistORM(artist_id=artist.artist_id)
            )
        
        # Добавляем жанры
        for genre in track.genres:
            track_orm.genres.append(
                TrackGenreORM(genre_id=genre.genre_id)
            )
        
        session.add(track_orm)
        await session.flush()
        await session.refresh(track_orm, ["artists", "genres"])
        return self._convert_to_domain(track_orm)

    @ConnectionDecorator()
    async def update(self, track: Track, session: AsyncSession | None = None) -> None:
        # Загружаем трек со всеми связями
        stmt = (
            select(TrackORM)
            .options(
                selectinload(TrackORM.artists),
                selectinload(TrackORM.genres)
            )
            .where(TrackORM.track_id == track.track_id)
        )
        result = await session.execute(stmt)
        track_orm = result.scalar_one()

        # Обновляем основные поля
        track_orm.title = track.title
        track_orm.duration_ms = track.duration.value
        track_orm.explicit = track.explicit
        track_orm.release_date = track.release_date

        # Обновляем артистов
        existing_artists = {ta.artist_id for ta in track_orm.artists}
        new_artists = {a.artist_id for a in track.artists}
        
        # Удаляем отсутствующих артистов
        for ta in track_orm.artists:
            if ta.artist_id not in new_artists:
                await session.delete(ta)
        
        # Добавляем новых артистов
        for artist in track.artists:
            if artist.artist_id not in existing_artists:
                track_orm.artists.append(
                    TrackArtistORM(artist_id=artist.artist_id)
                )

        # Обновляем жанры (аналогично артистам)
        existing_genres = {tg.genre_id for tg in track_orm.genres}
        new_genres = {g.genre_id for g in track.genres}
        
        for tg in track_orm.genres:
            if tg.genre_id not in new_genres:
                await session.delete(tg)
        
        for genre in track.genres:
            if genre.genre_id not in existing_genres:
                track_orm.genres.append(
                    TrackGenreORM(genre_id=genre.genre_id)
                )

        await session.flush()

    def _convert_to_domain(self, track_orm: TrackORM) -> Track:
        """Конвертирует ORM модель в доменный объект"""
        return Track(
            track_id=track_orm.track_id,
            title=track_orm.title,
            duration=DurationMs(value=track_orm.duration_ms),
            artists=[
                ArtistInfo(
                    artist_id=ta.artist.artist_id,
                    name=ta.artist.name,
                    is_verified=ta.artist.verified
                )
                for ta in track_orm.artists
            ] if track_orm.artists else [],
            genres=[
                Genre(
                    genre_id=tg.genre.genre_id,
                    name=tg.genre.name
                )
                for tg in track_orm.genres
            ] if track_orm.genres else [],
            explicit=track_orm.explicit,
            release_date=track_orm.release_date,
            created_at=track_orm.created_at
        )