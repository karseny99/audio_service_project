import re
import bcrypt
from dataclasses import dataclass
from src.core.exceptions import ValueObjectException
from passlib.hash import bcrypt

from dataclasses import dataclass, field
from passlib.hash import bcrypt
from typing import Any

@dataclass(frozen=True)
class PasswordHash:
    """
    VO для пароля: сразу хэширует сырой пароль или
    принимает уже готовый хэш (через флаг already_hashed).
    """
    _hash: str = field(init=False, repr=False)

    def __init__(self, raw_or_hashed: str, already_hashed: bool = False) -> None:
        if already_hashed:
            h = raw_or_hashed
        else:
            h = bcrypt.hash(raw_or_hashed)
        # обходим frozen инициализацию
        object.__setattr__(self, "_hash", h)

    @property
    def value(self) -> str:
        return self._hash

    def verify(self, raw: str) -> bool:
        return bcrypt.verify(raw, self._hash)

    def __str__(self) -> str:
        return self._hash