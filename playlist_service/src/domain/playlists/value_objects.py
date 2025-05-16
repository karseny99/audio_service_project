from dataclasses import dataclass
from typing import NewType

from src.core.exceptions import ValueObjectException

TrackId = NewType('TrackId', int)
UserId = NewType('UserId', int)

@dataclass(frozen=True)
class PlaylistTitle:
    value: str
    
    def __post_init__(self):
        if len(self.value) not in range(1, 100):
            print(len(self.value))
            raise ValueObjectException("Empty or too long title's length")
        

