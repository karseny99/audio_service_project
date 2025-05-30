import asyncio
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from datetime import datetime

class StreamStatus(Enum):
    SHOULD_RESTART = auto()
    STARTED = auto()
    PAUSED = auto()
    FINISHED = auto()

@dataclass
class AudioTrack:
    track_id: str
    total_chunks: int  # Общее количество чанков (из proto)
    available_bitrates: list[str]  # ["128kbps", "320kbps"]
    duration_ms: int  # Полная длительность трека в мс

@dataclass
class StreamSession:
    session_id: str
    user_id: str
    track: AudioTrack  # Вместо track_id + total_chunks
    current_bitrate: str
    status: StreamStatus
    current_chunk: int  # Текущий отправленный чанк (0-based)
    started_at: datetime
    paused_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    message_queue: asyncio.Queue = None  
    pause_event: asyncio.Event = None    


@dataclass
class AudioChunk:
    data: bytes
    number: int  # Порядковый номер (соответствует current_chunk сессии)
    is_last: bool
    bitrate: str 