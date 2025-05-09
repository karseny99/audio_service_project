# src/domain/users/value_objects/password_hash.py
from passlib.hash import bcrypt
from dataclasses import dataclass, field

@dataclass(frozen=True)
class PasswordHash:
    _hash: str = field(init=False, repr=False)

    def __init__(self, raw_or_hashed: str, already_hashed: bool = False):
        if already_hashed:
            h = raw_or_hashed
        else:
            h = bcrypt.hash(raw_or_hashed)
        object.__setattr__(self, "_hash", h)

    @property
    def value(self) -> str:
        return self._hash

    def verify(self, raw: str) -> bool:
        return bcrypt.verify(raw, self._hash)

    def __str__(self) -> str:
        return self._hash
