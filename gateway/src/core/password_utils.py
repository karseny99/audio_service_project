from passlib.hash import bcrypt
from src.core.config import settings
import os

from passlib.hash import pbkdf2_sha256

FIXED_SALT = os.urandom(16).hex()

def hash_password(password: str) -> str:
    return pbkdf2_sha256.using(
        salt=FIXED_SALT.encode(),
        rounds=310000 
    ).hash(password)
