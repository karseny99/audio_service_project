from dataclasses import dataclass
from src.core.exceptions import ValueObjectException

@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if len(self.value) not in range(3, 16) :
            raise ValueObjectException("Bad username's length")
        if not self.value.isalnum():
            raise ValueObjectException("Username must contain only digits or letters")
