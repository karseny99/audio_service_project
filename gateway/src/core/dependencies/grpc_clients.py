import grpc
from functools import lru_cache

from src.core.config import settings
from src.protos.listening_history_context.generated import LikeCommands_pb2, LikeCommands_pb2_grpc
from src.protos.user_context.generated import commands_pb2_grpc, track_pb2_grpc, track_search_pb2_grpc

@lru_cache(maxsize=None)
def get_track_search_channel() -> grpc.Channel:
    return grpc.insecure_channel(
        settings.TRACK_SEARCH_GRPC_URL,
        options=[('grpc.keepalive_time_ms', 10000)]
    )

def get_track_search_stub():
    channel = get_track_search_channel()
    return track_search_pb2_grpc.TrackSearchServiceStub(channel)

@lru_cache(maxsize=None)  # Кешируем канал на всё время работы приложения
def get_user_channel() -> grpc.Channel:
    return grpc.insecure_channel(
        settings.get_grpc_url(),  
        options=[
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.enable_retries', 1),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50MB
        ]
    )

def get_user_command_stub():
    channel = get_user_channel()
    return commands_pb2_grpc.UserCommandServiceStub(channel)


@lru_cache(maxsize=None)
def get_music_catalog_channel() -> grpc.Channel:
    return grpc.insecure_channel(
        settings.MUSIC_CATALOG_GRPC_URL,
        options=[
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ]
    )

def get_music_catalog_stub():
    channel = get_music_catalog_channel()
    return track_pb2_grpc.TrackQueryServiceStub(channel)

@lru_cache(maxsize=None)
def get_listening_history_channel() -> grpc.Channel:
    return grpc.insecure_channel(
        settings.LISTENING_HISTORY_GRPC_URL,
        options=[
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ]
    )

def get_listening_stub():
    channel = get_listening_history_channel()
    return LikeCommands_pb2_grpc.LikeCommandServiceStub(channel)