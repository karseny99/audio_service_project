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
import random

if __name__ == "__main__":
    user_id = register_user(
        username=f"{random.randint(1, 10**10)}",
        email=f"john@example.com{random.randint(1, 10**10)}",
        password="secure123"
    )
    print(f"Registered user ID: {user_id}")