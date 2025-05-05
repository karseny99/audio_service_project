import re
from dataclasses import dataclass
from src.core.exceptions import ValueObjectException

@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueObjectException("Invalid email format")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))