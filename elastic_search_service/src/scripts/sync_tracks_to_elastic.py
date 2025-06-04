import asyncio
from src.core.di import Container
from src.core.config import settings
from src.core.logger import logger
import asyncpg

async def sync_tracks():
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB
    )
    
    tracks = await conn.fetch("""
        SELECT 
            t.track_id,
            t.title,
            t.duration_ms,
            t.explicit,
            t.release_date,
            array_agg(DISTINCT a.name) AS artists,
            array_agg(DISTINCT g.name) AS genres
        FROM music_catalog.tracks t
        LEFT JOIN music_catalog.track_artists ta ON t.track_id = ta.track_id
        LEFT JOIN music_catalog.artists a ON ta.artist_id = a.artist_id
        LEFT JOIN music_catalog.track_genres tg ON t.track_id = tg.track_id
        LEFT JOIN music_catalog.genres g ON tg.genre_id = g.genre_id
        GROUP BY t.track_id
    """)
    
    await Container.init_resources()
    es_client = Container.elastic_client().client
    repo = Container.search_repository()
    
    actions = []
    for track in tracks:
        raw_artists = track["artists"] or []
        raw_genres  = track["genres"]  or []

        # Фильтруем все None, оставляем только строки
        artists = [a for a in raw_artists if isinstance(a, str)]
        genres  = [g for g in raw_genres  if isinstance(g, str)]


        doc = {
            "track_id":     track["track_id"],
            "title":        track["title"],
            "duration_ms":  track["duration_ms"],
            "artists":      artists,
            "genres":       genres,
            "explicit":     track["explicit"],
            # Если release_date == None, положим None
            "release_date": track["release_date"].isoformat() if track["release_date"] else None
        }
        actions.append({
            "_index": settings.ELASTIC_TRACK_INDEX,
            "_id": str(track["track_id"]),
            "_source": doc
        })
    
    if actions:
        await repo.bulk_index(actions)
        logger.info(f"Indexed {len(actions)} tracks to Elasticsearch")
    else:
        logger.warning("No tracks found to index")
    
    await conn.close()
    await Container.shutdown_resources()

if __name__ == "__main__":
    asyncio.run(sync_tracks())