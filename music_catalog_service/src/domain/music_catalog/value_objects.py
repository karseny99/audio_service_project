from dataclasses import dataclass
from typing import NewType

from src.core.exceptions import ValueObjectException

# Идентификаторы
TrackId = NewType('TrackId', int)
ArtistId = NewType('ArtistId', int)
GenreId = NewType('GenreId', int)

class Bitrate:
    SUPPORTED = [128, 192, 320]

    def __init__(self, value: int):
        if value not in self.SUPPORTED:
            raise ValueObjectException("Unsupported bitrate")
        self.value = value

@dataclass(frozen=True)
class DurationMs:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueObjectException("Duration must be positive")

@dataclass(frozen=True)
class TrackTitle:
    value: str

    def __post_init__(self):
        if len(self.value) not in range(1, 256):
            raise ValueObjectException("Bad track's length")