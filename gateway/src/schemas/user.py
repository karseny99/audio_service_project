# gateway/src/schemas/user.py

from pydantic import BaseModel, EmailStr, constr

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