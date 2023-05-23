from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from pydantic.types import date

from src.database.models import Role



class UserModel(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    created_at: date

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"

    class Config:
        orm_mode = True


# class UserProfileResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     avatar: str
#     is_active: bool
#     created_at: datetime


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UpdateUser(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator('email', pre=True, always=True)
    def remove_empty_email(cls, v):
        return EmailStr(v) if v is not None and v != "" else None

    @validator('username', pre=True, always=True)
    def remove_empty_username(cls, v):
        return v if v is not None and v != "" else None


class UserBanned(BaseModel):
    user: UserDb
    detail: str = "User successfully banned"


class UserInfoResponse(BaseModel):
    username: str
    created_at: date
    images_count: int


class RequestRole(BaseModel):
    email: EmailStr
    roles: Role



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


class ImageBase(BaseModel):
    image_url: str = Field(max_length=500)
    description: Optional[str] = Field(max_length=500)


class ImageModel(ImageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int

    class Config:
        orm_mode = True


class ImageResponseCreated(ImageModel):
    detail: str = "Image successfully created"

    class Config:
        orm_mode = True


class ImageResponseUpdated(ImageModel):
    detail: str = "Image description successfully updated"

    class Config:
        orm_mode = True


class ImageResponseEdited(ImageModel):
    detail: str = "Image successfully edited"

    class Config:
        orm_mode = True


# class TagModelAddToPicture(BaseModel):
#     tag1: str = ''
#     tag2: str = ''
#     tag3: str = ''
#     tag4: str = ''
#     tag5: str = ''
#
#     def to_list(self):
#         return [self.tag1, self.tag2, self.tag3, self.tag4, self.tag5]


