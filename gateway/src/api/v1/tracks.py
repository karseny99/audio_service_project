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

from src.schemas.track import (
    TracksByArtistRequest,
    TracksByGenreRequest,
    TracksPaginationResponse,
    TrackResponse,
    TrackSearchRequest,
    TrackSearchResponse,
    TrackItemResponse
)
from src.protos.user_context.generated import track_search_pb2

router = APIRouter(prefix="/tracks", tags=["Tracks"])

@router.post("/search", response_model=TrackSearchResponse)
@inject
async def search_tracks(
    request: TrackSearchRequest,
    stub=Depends(Provide[Container.track_search_stub])
):
    # Создаем gRPC запрос, преобразуя None в пустые значения
    grpc_request = track_search_pb2.SearchTracksRequest(
        title=request.title or "",
        artist_name=request.artist_name or "",
        genre_name=request.genre_name or [],
        min_duration_ms=request.min_duration_ms or 0,
        max_duration_ms=request.max_duration_ms or 0,
        explicit=request.explicit if request.explicit is not None else None,
        release_date_from=request.release_date_from.isoformat() if request.release_date_from else "",
        release_date_to=request.release_date_to.isoformat() if request.release_date_to else "",
        page=request.page,
        page_size=request.page_size
    )
    
    try:
        response = stub.Search(grpc_request)
        return TrackSearchResponse(
            tracks=[
                TrackItemResponse(
                    track_id=t.track_id,
                    title=t.title,
                    duration_ms=t.duration_ms,
                    artists=list(t.artists),
                    genres=list(t.genres),
                    explicit=t.explicit,
                    release_date=t.release_date
                ) for t in response.tracks
            ],
            total=response.total,
            page=response.page,
            page_size=response.page_size
        )
    except Exception as e:
        # logger.error(f"Search error: {str(e)}")
        raise HTTPException(500, detail="Internal server error")

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
        
        response = stub.GetTracksByArtist(grpc_request)
        
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
        
        response = stub.GetTracksByGenre(grpc_request)
        
        return TracksPaginationResponse(
            tracks=[TrackResponse(**track.__dict__) for track in response.tracks],
            total=response.pagination.total,
            offset=request.offset,
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, detail=str(e))