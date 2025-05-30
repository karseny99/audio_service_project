from typing import AsyncGenerator
from src.domain.stream.repository import AudioStreamer
from src.domain.stream.models import StreamSession

class GetChunkGeneratorUseCase:
    def __init__(self, audio_streamer: AudioStreamer):
        self._audio_streamer = audio_streamer

    def execute(
        self, 
        session: StreamSession,
    ) -> AsyncGenerator[bytes, None]:

        if not self._audio_streamer

        self._audio_streamer.switch_bitrate(session.current_bitrate)
        self._audio_streamer.seek(session.current_chunk)
        return self._audio_streamer.chunks()
