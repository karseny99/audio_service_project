# gateway/src/schemas/user.py

from pydantic import BaseModel, EmailStr, constr, Field
from typing import List
from datetime import datetime

class RegisterUserRequest(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6)

class LoginUserRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: constr(min_length=6)

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr

class LoginUserResponse(BaseModel):
    access_token: str
    token_type: str

class ChangePasswordResponse(BaseModel):
    status: str

class RegisterUserResponse(BaseModel):
    status: str
    user_id: int

class GetUserInfoResponse(BaseModel):
    status : str
    id: str
    username: str
    email: EmailStr
    created_at : datetime

class GetUserLikesRequest(BaseModel):
    limit: int = Field(10, ge=1, le=100, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение")

class GetUserLikesResponse(BaseModel):
    tracks: List[int] = Field(..., description="Список ID треков")

class GetUserHistoryRequest(BaseModel):
    limit: int = Field(10, ge=1, le=100, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение")

class GetUserHistoryResponse(BaseModel):
    tracks: List[int] = Field(..., description="Список треков в истории")

class LikeTrackRequest(BaseModel):
    track_id: int = Field(..., gt=0, description="ID трека")

