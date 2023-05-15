from pydantic import BaseModel, Field, EmailStr
from pydantic.types import date

from src.database.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    class UserResponse(BaseModel):
        user: UserDb
        detail: str = "User successfully created"

    class Config:
        orm_mode = True


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
