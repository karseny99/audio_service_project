import grpc
from functools import lru_cache

from src.core.config import settings

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
