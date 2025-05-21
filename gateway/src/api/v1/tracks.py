from fastapi import APIRouter, Depends, HTTPException, Query
from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.services.music_catalog_service import (
    get_tracks_by_artist,
    get_tracks_by_genre
)

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.get("/artist/{artist_id}")
@inject
async def get_tracks_by_artist_endpoint(
    artist_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    stub=Depends(Provide[Container.music_catalog_stub])
):
    try:
        response = get_tracks_by_artist(artist_id, offset, limit)
        return {
            "tracks": response.tracks,
            "total": response.total
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.get("/genre/{genre_id}")
@inject
async def get_tracks_by_genre_endpoint(
    genre_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    stub=Depends(Provide[Container.music_catalog_stub])
):
    try:
        response = get_tracks_by_genre(genre_id, offset, limit)
        return {
            "tracks": response.tracks,
            "total": response.total
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))