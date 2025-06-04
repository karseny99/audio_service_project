from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from src.services.playlist_service import add_playlist
from src.schemas.playlist import AddPlaylistRequest, AddPlaylistResponse

router = APIRouter(prefix="/playlists", tags=["Playlists"])

@router.post(
    "/add",
    summary="Add a public playlist",
    status_code=status.HTTP_200_OK
)
@inject
async def add_playlist_endpoint(
        payload: AddPlaylistRequest,  
        request: Request,
):
    user_id: str = request.state.user_id
    try:
        add_playlist(
            user_id=user_id,
            playlist_id=payload.playlist_id
        )
        resp = AddPlaylistResponse(
            status="added"
        )
        return resp
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
