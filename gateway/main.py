# from fastapi import FastAPI
# from api.v1 import users, playlists

# app = FastAPI()
# app.include_router(users.router)
# app.include_router(playlists.router)

'''

    #
    #   Пример для оптимизированного вызова grpc
    #

    # В FastAPI роутере 
    from fastapi import Depends

    async def get_user_stub():
        channel = get_user_channel()
        return commands_pb2_grpc.UserCommandServiceStub(channel)

    from fastapi import FastAPI
    from core.middleware.logging import log_requests
    from core.logger import setup_logging

    app = FastAPI()
    setup_logging(settings.LOKI_URL)  # LOKI_URL из env-переменных

    # Подключение middleware
    app.middleware("http")(log_requests)


        
    @router.post("/register")
    async def register(
        stub: UserCommandServiceStub = Depends(get_user_stub)
    ):
        await stub.RegisterUser(...)

'''

from src.services.user_service import register_user
from src.core.middleware.auth import AuthMiddleware
import random


from fastapi import FastAPI
from src.core.container import Container
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
import uvicorn

app = FastAPI(title="API Gateway")
container = Container()
app.container = container
app.include_router(auth_router)
app.include_router(users_router)
app.add_middleware(AuthMiddleware)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")

# if __name__ == "__main__":
#     user_id = register_user(
#         username=f"{random.randint(1, 10**10)}",
#         email=f"john@example.com{random.randint(1, 10**10)}",
#         password="secure123"
#     )
#     print(f"Registered user ID: {user_id}")