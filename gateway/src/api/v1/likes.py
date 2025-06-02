from fastapi import APIRouter, HTTPException, status, Request

from src.core.logger import logger
from src.services.user_service import get_user_history, get_user_likes, like_track
from src.schemas.user import (
    GetUserLikesResponse, 
    GetUserLikesRequest,
    GetUserHistoryResponse, 
    GetUserHistoryRequest, 
    LikeTrackRequest
)

router = APIRouter(prefix="/users", tags=["Likes"])

@router.get(
    "/{user_id}/likes",
    response_model=GetUserLikesResponse,
    summary="Получить лайки пользователя",
    description="Возвращает список треков, которые лайкнул пользователь",
)
async def get_user_likes_endpoint(
    payload: GetUserLikesRequest,
    request: Request,
):
    try:
        user_id = request.state.user_id
        result = get_user_likes(user_id=int(user_id), limit=int(payload.limit), offset=int(payload.offset))
        return GetUserLikesResponse(tracks=result['tracks'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/{user_id}/history",
    response_model=GetUserHistoryResponse,
    summary="Получить историю прослушиваний пользователя",
    description="Возвращает историю прослушиваний треков пользователя",
)
async def get_user_history_endpoint(
    payload: GetUserHistoryRequest,
    request: Request,
):
    try:
        user_id = request.state.user_id
        grpc_response = get_user_history(user_id=int(user_id), limit=int(payload.limit), offset=int(payload.offset))
        
        return GetUserHistoryResponse(
            tracks=[
                track_id
                for track_id in grpc_response.get("tracks", [])
            ]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/tracks/{track_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Поставить лайк треку",
    description="Добавляет трек в понравившиеся для указанного пользователя",
)
async def like_track_endpoint(
    track_id: int,
    request: Request,
):
    try:
        like_track(
            user_id=request.state.user_id,
            track_id=track_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        if "недоступен" in str(e):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
