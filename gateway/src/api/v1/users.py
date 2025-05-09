from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
import grpc

from src.core.container import Container
from src.services.user_service import register_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register_user_endpoint(
    username: str,
    email: str,
    password: str,
    stub=Depends(Provide[Container.user_stub]),  # если нужен stub из DI
):
    try:
        user_id = register_user(username, email, password)
        return {"status": "created", "user_id": user_id}

    except ValueError as e:
        # сюда упадут ошибки валидации (INVALID_ARGUMENT) или ALREADY_EXISTS
        detail = str(e)
        if "validation" in detail.lower() or "ошибка валидации" in detail.lower():
            http_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            http_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=http_code, detail=detail)

    except grpc.RpcError as e:
        # любые необработанные gRPC-ошибки
        code = e.code()
        if code == grpc.StatusCode.UNAVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service is unavailable"
            )
        # прочие gRPC ошибки
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"gRPC error: {code.name}"
        )

    except Exception as e:
        # ловим всё остальное
        raise HTTPException(status_code=500, detail="Unexpected error")
