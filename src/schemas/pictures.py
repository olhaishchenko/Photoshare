from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ImageCircleModel(BaseModel):
    use_filter: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class ImageEffectModel(BaseModel):
    use_filter: bool = False
    art_audrey: bool = False
    art_zorro: bool = False
    cartoonify: bool = False
    blur: bool = False
    

class ImageResizeModel(BaseModel):
    use_filter: bool = False
    crop: bool = False
    fill: bool = False
    height: int = Field(ge=0, default=400)
    width: int = Field(ge=0, default=400)


class ImageRotateModel(BaseModel):
    use_filter: bool = False
    width: int = Field(ge=0, default=400)
    degree: int = Field(ge=-360, le=360, default=45)


class EditImageModel(BaseModel):
    circle: ImageCircleModel
    effect: ImageEffectModel
    resize: ImageResizeModel
    rotate: ImageRotateModel


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