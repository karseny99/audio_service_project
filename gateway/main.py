# # from fastapi import FastAPI
# # from api.v1 import users, playlists

# # app = FastAPI()
# # app.include_router(users.router)
# # app.include_router(playlists.router)

# '''

#     #
#     #   Пример для оптимизированного вызова grpc
#     #

#     # В FastAPI роутере 
#     from fastapi import Depends

#     async def get_user_stub():
#         channel = get_user_channel()
#         return commands_pb2_grpc.UserCommandServiceStub(channel)

#     from fastapi import FastAPI
#     from core.middleware.logging import log_requests
#     from core.logger import setup_logging

#     app = FastAPI()
#     setup_logging(settings.LOKI_URL)  # LOKI_URL из env-переменных

#     # Подключение middleware
#     app.middleware("http")(log_requests)


        
#     @router.post("/register")
#     async def register(
#         stub: UserCommandServiceStub = Depends(get_user_stub)
#     ):
#         await stub.RegisterUser(...)

# '''

# from src.services.user_service import register_user
# from src.core.middleware.auth import AuthMiddleware
# import random


# from fastapi import FastAPI
# from src.core.container import Container
# from src.api.v1.auth import router as auth_router
# from src.api.v1.users import router as users_router
# import uvicorn

# app = FastAPI(title="API Gateway")
# container = Container()
# app.container = container
# app.include_router(auth_router)
# app.include_router(users_router)
# app.add_middleware(AuthMiddleware)


# if __name__ == "__main__":

#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="info",
#         access_log=True,
#         reload=True,
#     )

# # if name == "main":
# #     user_id = register_user(
# #         username=f"{random.randint(1, 10**10)}",
# #         email=f"john@example.com{random.randint(1, 10**10)}",
# #         password="secure123"
# #     )
# #     print(f"Registered user ID: {user_id}")

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.services.user_service import register_user
from src.core.middleware.auth import AuthMiddleware
from src.core.container import Container
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
import uvicorn

app = FastAPI(title="API Gateway")

# DI контейнер
container = Container()
app.container = container

# Подключение роутеров
app.include_router(auth_router)
app.include_router(users_router)

# Мидлварь авторизации
app.add_middleware(AuthMiddleware)

# ✅ Кастомная OpenAPI-схема для добавления BearerAuth
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API Gateway",
        version="0.1.0",
        description="API Gateway for Audio Service",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=True,
    )