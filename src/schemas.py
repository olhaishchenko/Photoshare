from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


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


class CommentBase(BaseModel):
    comment: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int
    image_id: int

    class Config:
        orm_mode = True


class CommentUpdate(CommentModel):
    updated_at = datetime

    class Config:
        orm_mode = True
