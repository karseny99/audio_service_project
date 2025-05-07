import grpc
from functools import lru_cache

from core.config import settings
from protos.user_context.generated import commands_pb2_grpc, commands_pb2

@lru_cache(maxsize=1)
def get_user_stub() -> commands_pb2_grpc.UserCommandServiceStub:
    """
    Один-единственный канал и stub на всё приложение.
    """
    channel = grpc.insecure_channel(
        settings.user_service_grpc_url,
        options=[
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.enable_retries", 1),
        ],
    )
    return commands_pb2_grpc.UserCommandServiceStub(channel)

async def register_user(
    username: str, email: str, password: str
) -> str:
    """
    Вызывает gRPC-метод RegisterUser и возвращает user_id.
    """
    stub = get_user_stub()
    req = commands_pb2.RegisterUserRequest(
        username=username, email=email, password=password
    )
    resp = stub.RegisterUser(req, timeout=10.0)
    return str(resp.user_id)
