from fastapi import APIRouter, Depends, HTTPException, status, Request
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from src.services.user_service import change_password
from src.schemas.user import ChangePasswordRequest


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
        return {"status": "password_changed"}
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
