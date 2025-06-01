from typing import AsyncGenerator
from src.domain.stream.repository import AudioStreamer
from src.domain.stream.models import StreamSession, AudioChunk
from src.core.logger import logger

class GetChunkGeneratorUseCase:
    def __init__(self, audio_streamer: AudioStreamer):
        self._audio_streamer = audio_streamer

    async def execute(self, session: StreamSession) -> AsyncGenerator[AudioChunk, None]:
        await self._audio_streamer.switch_bitrate(session.current_bitrate)
        current_offset = session.current_chunk * self._audio_streamer.chunk_size
        
        async for chunk in self._audio_streamer.chunks(start_pos=current_offset):
            session.total_chunks_sent += 1
            session.current_chunk = chunk.number
            yield chunk
