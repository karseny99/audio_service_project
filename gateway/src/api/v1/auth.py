from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from src.core.jwt_utils import create_access_token, verify_token
from src.core.container import Container
from src.services.user_service import register_user, authenticate_user
from src.schemas.user import RegisterUserRequest, RegisterUserResponse, LoginUserRequest, LoginUserResponse
import grpc

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
async def register_user_endpoint(
    req: RegisterUserRequest,
    stub=Depends(Provide[Container.user_stub]),  # если нужен stub из DI
):
    try:
        user_id = register_user(req.username, req.email, req.password)
        resp = RegisterUserResponse(
            status="created",
            user_id=user_id
        )
        return resp

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

@router.post("/login", summary="Authenticate user and return JWT")
def login(req: LoginUserRequest):
    try:
        user_id = authenticate_user(req.username, req.password)
        token = create_access_token(user_id)
        resp = LoginUserResponse(
            access_token=token,
            token_type="bearer"
        )
        return resp
    
    except ValueError as e:
        # 404 vs 401 по тексту
        msg = str(e)
        if "не найден" in msg.lower():
            code = status.HTTP_404_NOT_FOUND
        else:
            code = status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=code, detail=msg)
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="UserService unavailable")