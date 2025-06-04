from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from src.services.user_service import change_password, get_user_info, get_user_likes, like_track
from src.schemas.user import ChangePasswordRequest, ChangePasswordResponse, GetUserInfoResponse, GetUserLikesResponse, GetUserLikesResponse, GetUserHistoryResponse, GetUserHistoryResponse, LikeTrackRequest
from src.core.logger import logger

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
        logger.debug(f"change password: {request}")
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


@router.get(  
    "/get-user-info",
    summary="Get user info",
    status_code=status.HTTP_200_OK
)
@inject
async def get_user_info_endpoint(
    request: Request,  
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

