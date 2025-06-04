import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from datetime import datetime

import uuid

from src.core.exceptions import BitrateNotFound

class StreamStatus(Enum):
    STARTED = auto()
    PAUSED = auto()
    STOPPED = auto()
    SHOULD_RESTART = auto()
    ARTIFICIAL_CHUNK = auto()


@dataclass
class AudioTrack:
    track_id: str
    total_chunks: int  # Общее количество чанков (из proto)
    available_bitrates: list[str]  # ["128kbps", "320kbps"]
    duration_ms: int  # Полная длительность трека в мс

@dataclass
class StreamSession:
    user_id: str
    track: AudioTrack
    current_bitrate: str
    chunk_size: int
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: StreamStatus = StreamStatus.STARTED
    current_chunk: int = 0
    total_chunks_sent: int = 0 
    started_at: datetime = datetime.now()
    paused_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    message_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    reader_task: Optional[asyncio.Task] = field(default=None, init=False)

    def pause(self):
        if self.status == StreamStatus.STARTED:
            self.status = StreamStatus.PAUSED
            self.paused_at = datetime.now()

    def resume(self):
        if self.status == StreamStatus.PAUSED:
            self.status = StreamStatus.STARTED
            self.paused_at = None

    def stop(self):
        self.status = StreamStatus.STOPPED

    def prestop(self):
        self.status = StreamStatus.ARTIFICIAL_CHUNK

    def should_stop(self) -> bool:
        return self.status == StreamStatus.ARTIFICIAL_CHUNK
    
    def should_continue(self) -> bool:
        """Проверяет, можно ли продолжать отправку чанков"""
        return self.status in (StreamStatus.STARTED, StreamStatus.SHOULD_RESTART, StreamStatus.ARTIFICIAL_CHUNK)

    def is_active(self) -> bool:
        """Проверяет, активна ли сессия (не остановлена и не завершена)"""
        return self.status != StreamStatus.STOPPED

    def cleanup(self):
        """Корректное завершение сессии"""
        if self.reader_task and not self.reader_task.done():
            self.reader_task.cancel()
        
        self.status = StreamStatus.STOPPED
        self.finished_at = datetime.now()

    def switch_bitrate(self, new_bitrate: str):
        if new_bitrate not in self.track.available_bitrates:
            raise BitrateNotFound(f"No such bitrate for track, available are {self.track.available_bitrates}")
        self.current_bitrate = new_bitrate


@dataclass
class AudioChunk:
    data: bytes
    number: int  # Порядковый номер (соответствует current_chunk сессии)
    is_last: bool
    bitrate: str 