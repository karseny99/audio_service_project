from typing import AsyncGenerator
from src.domain.stream.repository import AudioStorage

class StreamChunksUseCase:
    def __init__(self, audio_storage: AudioStorage):
        self.audio_storage = audio_storage

    async def execute(
        self, 
        track_id: str, 
        bitrate: int, 
        offset: int = 0
    ) -> AsyncGenerator[bytes, None]:
        """Возвращает асинхронный генератор чанков аудио."""
        if not track_id or bitrate <= 0:
            raise ValueError("Invalid track_id or bitrate")

        async for chunk in self.audio_storage.get_chunks(
            track_id=track_id,
            bitrate=bitrate,
            offset=offset
        ):
            yield chunk