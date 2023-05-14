from typing import Optional

from fastapi import Depends
from pydantic import BaseModel, Field, EmailStr, validator
from pydantic.types import date


class UserModel(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)
    created_at: date


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: date

    class Config:
        orm_mode = True


class UpdateUser(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr] = None

    @validator('email', pre=True, always=True)
    def remove_empty_email(cls, v):
        return EmailStr(v) if v is not None and v != "" else None

    @validator('username', pre=True, always=True)
    def remove_empty_username(cls, v):
        return v if v is not None and v != "" else None


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class UserBanned(BaseModel):
    user: UserDb
    detail: str = "User successfully banned"


class UserInfoResponse(BaseModel):
    username: str
    created_at: date
    images_count: int
