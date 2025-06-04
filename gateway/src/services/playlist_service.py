import sys
from grpc import RpcError, StatusCode
from src.core.dependencies.grpc_clients import get_playlist_stub
from src.protos.user_context.generated import PlaylistCommands_pb2, PlaylistCommands_pb2_grpc

def add_playlist(user_id: str, playlist_id: str) -> None:
    """
    Добавление публичного плейлиста через gRPC

    Raises:
        ValueError: если неверные креды или плейлист не найден
        RuntimeError: все остальные ошибки
    """
    stub = get_playlist_stub()
    request = PlaylistCommands_pb2.AddPlaylistRequest(
        user_id=user_id,
        playlist_id=playlist_id
    )
    try:
        stub.AddPlaylist(request, timeout=5.0)
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


def create_playlist(user_id: str, title: str, is_public: bool) -> str:
    """
    Создание плейлиста через gRPC

    Returns:
        str: playlist_id

    Raises:
        ValueError: если неверные креды
        RuntimeError: все остальные ошибки
    """
    stub = get_playlist_stub()
    request = PlaylistCommands_pb2.CreatePlaylistRequest(
        user_id=user_id,
        title=title,
        is_public=is_public
    )
    try:
        response = stub.CreatePlaylist(request, timeout=10.0)
        return str(response.playlist_id)
    except RpcError as e:
        code = e.code()
        if code == StatusCode.INVALID_ARGUMENT:
            raise ValueError(f"Ошибка валидации: {e.details()}")
        elif code == StatusCode.UNAVAILABLE:
            raise RuntimeError("Сервис плейлистов недоступен")
        else:
            raise RuntimeError(f"Ошибка gRPC: {code.name}")
