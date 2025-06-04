# gateway/src/core/jwt_utils.py

import jwt
from datetime import datetime, timedelta
from pydantic_settings import BaseSettings

class JWTSettings(BaseSettings):
    SECRET_KEY: str = "supersecrett"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240

jwt_settings = JWTSettings()

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=jwt_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, jwt_settings.SECRET_KEY, algorithm=jwt_settings.ALGORITHM)

def verify_token(token: str) -> str:
    payload = jwt.decode(token, jwt_settings.SECRET_KEY, algorithms=[jwt_settings.ALGORITHM])
    return payload.get("sub")
