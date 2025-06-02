import sys
from grpc import RpcError, StatusCode
from src.core.dependencies.grpc_clients import get_user_command_stub
from src.protos.user_context.generated import commands_pb2, commands_pb2_grpc
from src.core.password_utils import hash_password

def add_playlist(user_id: str, playlist_id: str) -> None:
    stub = get_playlist_command_stub()
    request = playlist_pb2.SubscribeToPlaylistRequest(
        user_id=user_id,
        playlist_id=playlist_id
    )
    try:
        stub.SubscribeToPlaylist(request, timeout=5.0)
    except RpcError as e:
        code = e.code()
        if code == StatusCode.NOT_FOUND:
            raise ValueError("Плейлист не найден")
        elif code == StatusCode.INVALID_ARGUMENT:
            raise ValueError(f"Ошибка валидации: {e.details()}")
        elif code == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис плейлистов недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {code.name}")
