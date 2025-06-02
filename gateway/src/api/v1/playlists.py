from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from src.services.playlist_service import add_playlist
from src.schemas.playlist import AddPlaylistRequest, AddPlaylistResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/subscribe",
    summary="Subscribe to a public playlist",
    status_code=status.HTTP_200_OK
)
@inject
async def subscribe_to_playlist_endpoint(
        payload: AddRequestModel,  # Pydantic-модель
        request: Request,
):
    user_id: str = request.state.user_id
    try:
        add_playlist(
            user_id=user_id,
            playlist_id=payload.playlist_id
        )
        return {"status": "subscribed"}
    
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
