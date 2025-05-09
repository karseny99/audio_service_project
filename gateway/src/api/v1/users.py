from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
import grpc

from src.core.container import Container
from src.services.user_service import register_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
@inject
async def register_user_endpoint(
    username: str,
    email: str,
    password: str,
    stub=Depends(Provide[Container.user_stub]),
):
    try:
        user_id = register_user(username, email, password)
        return {"status": "created", "user_id": user_id}
    except grpc.RpcError as e:
        # сюда попадут INVALID_ARGUMENT / ALREADY_EXISTS и т.д.
        code = e.code()
        if code.name in ("INVALID_ARGUMENT", "ALREADY_EXISTS"):
            raise HTTPException(status_code=400, detail=e.details())
        raise HTTPException(status_code=502, detail="UserService unavailable")
