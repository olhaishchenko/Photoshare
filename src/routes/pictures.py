from fastapi import Depends, status, APIRouter, UploadFile, File, Query
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from src.database.db import get_db
from src.database.models import User
from src.schemas import ImageResponse
from src.services.auth import auth_service
from src.repository import pictures as repository_pictures
from src.services.cloud_image import CloudImage



router = APIRouter(prefix="/pictures", tags=['pictures'])


@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(description: str,
                       image_file: UploadFile = File(),
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    '''
    The **create_image** function creates a new image in the database.
    It takes a description and an image file as input.
    The image file is uploaded to Cloudinary and the url is stored in the database.
    
    :param description: str: The description of the image
    :param image_file: UploadFile: The image file
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    file_name = CloudImage.generate_name_image()
    CloudImage.upload(image_file.file, file_name, overwrite=False)
    image_url = CloudImage.get_url_for_image(file_name)
    image = await repository_pictures.create(description, image_url, current_user, db)
    return image


@router.get("/", response_model=List[ImageResponse], status_code=status.HTTP_200_OK)
async def get_images(limit: int = Query(10, le=50), offset: int = 0,
                     current_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    '''
    The **get_images** function gets all the images from the database.
    
    :param limit: int: The number of images to return
    :param offset: int: The number of images to skip
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A list of image objects
    '''
    images = await repository_pictures.get_images(limit, offset, current_user, db)
    if images is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return images


@router.get("/{image_id}", response_model=ImageResponse, status_code=status.HTTP_200_OK)
async def get_image(image_id: int,
                    current_user: User = Depends(auth_service.get_current_user),
                    db: Session = Depends(get_db)):
    '''
    The **get_image** function gets a single image from the database.

    :param image_id: int: The id of the image to return
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await repository_pictures.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_image(image_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    '''
    The **remove_image** function deletes a single image from the database.
    
    :param image_id: int: The id of the image to delete
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await repository_pictures.remove(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image