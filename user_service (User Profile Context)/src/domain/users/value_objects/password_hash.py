from passlib.hash import bcrypt
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordHash:
    _hash: str
    
    def __init__(self, hashed: str):
        h = hashed
        object.__setattr__(self, "_hash", h) 
    
    @property
    def value(self) -> str:
        return self._hash