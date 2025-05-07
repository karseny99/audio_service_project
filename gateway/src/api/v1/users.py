from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from grpc import RpcError

from core.container import Container
from grpc_clients.user_client import register_user

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
        # register_user использует cached stub
        user_id = await register_user(username, email, password)
        return {"status": "created", "user_id": user_id}
    except RpcError as e:
        # сюда попадут INVALID_ARGUMENT / ALREADY_EXISTS и т.д.
        code = e.code()
        if code.name in ("INVALID_ARGUMENT", "ALREADY_EXISTS"):
            raise HTTPException(status_code=400, detail=e.details())
        raise HTTPException(status_code=502, detail="UserService unavailable")
