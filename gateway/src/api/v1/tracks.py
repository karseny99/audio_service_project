from src.protos.user_context.generated.track_pb2 import (
    GetTracksByArtistRequest,
    GetTracksByGenreRequest,
    Pagination
)
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.schemas.track import (
    TracksByArtistRequest,
    TracksByGenreRequest,
    TracksPaginationResponse,
    TrackResponse
)

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.get("/artist", response_model=TracksPaginationResponse)
@inject
async def get_tracks_by_artist_endpoint(
    request: TracksByArtistRequest,
    stub=Depends(Provide[Container.music_catalog_stub])
):
    try:
        grpc_request = GetTracksByArtistRequest(
            artist_id=request.artist_id,
            pagination=Pagination(
                offset=request.offset,
                limit=request.limit
            )
        )
        
        response = await stub.GetTracksByArtist(grpc_request)
        
        return TracksPaginationResponse(
            tracks=[TrackResponse(**track.__dict__) for track in response.tracks],
            total=response.pagination.total,
            offset=request.offset,
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.get("/genre", response_model=TracksPaginationResponse)
@inject
async def get_tracks_by_genre_endpoint(
    request: TracksByGenreRequest,
    stub=Depends(Provide[Container.music_catalog_stub])
):
    try:
        grpc_request = GetTracksByGenreRequest(
            genre_id=request.genre_id,
            pagination=Pagination(
                offset=request.offset,
                limit=request.limit
            )
        )
        
        response = await stub.GetTracksByGenre(grpc_request)
        
        return TracksPaginationResponse(
            tracks=[TrackResponse(**track.__dict__) for track in response.tracks],
            total=response.pagination.total,
            offset=request.offset,
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))