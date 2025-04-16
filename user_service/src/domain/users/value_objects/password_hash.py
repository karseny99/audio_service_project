import re
import bcrypt
from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordHash:
    value: str  # Stores the hashed password
    
    # BCrypt pattern: starts with $2a$, $2b$, $2y$ followed by cost factor and hash
    _BCRYPT_PATTERN = re.compile(r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$')
    
    def __post_init__(self):
        """
            Validate that the value is a proper bcrypt hash
        """
        if not self._is_valid_bcrypt_hash(self.value):
            raise ValueError("Invalid bcrypt hash format")
       
    def verify(self, raw_password: str) -> bool:
        """
            Verify if raw password matches this hash
        """
        try:
            return bcrypt.checkpw(
                raw_password.encode('utf-8'),
                self.value.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _is_valid_bcrypt_hash(hash_str: str) -> bool:
        """
            Check if string matches bcrypt format
        """
        return bool(PasswordHash._BCRYPT_PATTERN.match(hash_str))
