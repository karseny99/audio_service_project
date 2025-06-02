from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from src.services.user_service import change_password, get_user_info, get_user_likes, like_track
from src.schemas.user import ChangePasswordRequest, ChangePasswordResponse, GetUserInfoResponse, GetUserLikesResponse, GetUserLikesResponse, GetUserHistoryResponse, GetUserHistoryResponse, LikeTrackRequest


router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/change-password",
    summary="Change own password",
    status_code=status.HTTP_200_OK
)
@inject
async def change_password_endpoint(
        payload: ChangePasswordRequest,
        request: Request,  # от AuthMiddleware в state.user_id
):
    user_id: str = request.state.user_id
    try:
        change_password(
            user_id=user_id,
            old_password=payload.old_password,
            new_password=payload.new_password
        )
        resp = ChangePasswordResponse(
            status="password_changed"
        )
        return resp
    
    except ValueError as e:
        # сюда попадут Invalid creds или Not found
        detail = str(e)
        code = status.HTTP_400_BAD_REQUEST
        if "не найден" in detail.lower():
            code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=detail)
    except RuntimeError as e:
        # сервис недоступен
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )


@router.get(  # в этом блоке не очень уверен 
    "/get-user-info",
    summary="Get user info",
    status_code=status.HTTP_200_OK
)
@inject
async def get_user_info_endpoint(
        request: Request,  # от AuthMiddleware в state.user_id
):
    user_id: str = request.state.user_id
    # user_id = int(request.state.user_id)
    try:
        user_info = get_user_info(
            user_id=user_id,
        )
        resp = GetUserInfoResponse(
            status="info_sent",
            id = user_id,
            username = user_info['username'],
            email = user_info['email'],
            created_at = user_info['created_at']
        )
        return resp
    
    except ValueError as e:
        # сюда попадут Invalid creds или Not found
        detail = str(e)
        code = status.HTTP_400_BAD_REQUEST
        if "не найден" in detail.lower():
            code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=detail)
    except RuntimeError as e:
        # сервис недоступен
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

@router.get(
    "/users/{user_id}/likes",
    response_model=GetUserLikesResponse,
    summary="Получить лайки пользователя",
    description="Возвращает список треков, которые лайкнул пользователь",
    tags=["Likes"]
)
async def get_user_likes(
    request: Request,
    limit: int = 10,
    offset: int = 0
):
    try:
        user_id = request.state.user_id
        result = get_user_likes(user_id=user_id, limit=limit, offset=offset)
        return GetUserLikesResponse(tracks=result['tracks'])
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get(
    "/users/{user_id}/history",
    response_model=GetUserHistoryResponse,
    summary="Получить историю прослушиваний пользователя",
    description="Возвращает историю прослушиваний треков пользователя",
    tags=["History"]
)
async def get_user_history(
    request: Request,
    limit: int = 10,
    offset: int = 0
):
    try:
        user_id = request.state.user_id
        grpc_response = get_user_history(user_id=user_id, limit=limit, offset=offset)
        
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
    tags=["Likes"]
)
async def like_track_endpoint(
    request: Request,
    track_id: int,
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
