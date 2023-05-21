from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field



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