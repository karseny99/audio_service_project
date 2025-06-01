from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.jwt_utils import verify_token
import re, jwt

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Пропускаем публичные пути
        if re.match(r"^/auth", path) or path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Missing or invalid Authorization header")
        token = auth_header[len("Bearer "):]
        try:
            user_id = verify_token(token)
            request.state.user_id = user_id
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid or expired token")

        return await call_next(request)