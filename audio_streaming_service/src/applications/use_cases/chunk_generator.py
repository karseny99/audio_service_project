from typing import AsyncGenerator
from src.domain.stream.repository import AudioStreamer
from src.domain.stream.models import StreamSession, AudioChunk

class GetChunkGeneratorUseCase:
    def __init__(self, audio_streamer: AudioStreamer):
        self._audio_streamer = audio_streamer

    async def execute(self, session: StreamSession) -> AsyncGenerator[AudioChunk, None]:
        self._audio_streamer.switch_bitrate(session.current_bitrate)
        self._audio_streamer.seek(session.current_chunk * self._audio_streamer.chunk_size)
        async for chunk in self._audio_streamer.chunks():
            yield chunk
