from fastapi import Depends, status, APIRouter, UploadFile, File, Query
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from src.database.db import get_db
from src.database.models import User
from src.schemas.pictures import ImageModel, ImageResponseCreated, ImageResponseEdited, ImageResponseUpdated
from src.schemas.pictures import EditImageModel
from src.services.auth import auth_service
from src.repository import pictures as repository_pictures
from src.services.cloud_image import CloudImage

router = APIRouter(prefix="/pictures", tags=['pictures'])


@router.post("/", response_model=ImageResponseCreated, status_code=status.HTTP_201_CREATED)
async def create_image(description: str,
                       tags: str = None,
                       image_file: UploadFile = File(...),
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The **create_image** function creates a new image in the database.
    It takes a description and an image file as input.
    The image file is uploaded to Cloudinary and the url is stored in the database.

    :param description: str: The description of the image
    :param tags: TagModelAddToPicture: 5 tags
    :param image_file: UploadFile: The image file
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """

    public_id = CloudImage.generate_name_image()
    CloudImage.upload(image_file.file, public_id, overwrite=False)
    image_url = CloudImage.get_url_for_image(public_id)
    image = await repository_pictures.create(description, tags, image_url, public_id, current_user, db)

    return image


@router.get("/", response_model=List[ImageModel], status_code=status.HTTP_200_OK)
async def get_images(limit: int = Query(10, le=50), offset: int = 0,
                     current_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The **get_images** function gets all the images from the database.

    :param limit: int: The number of images to return
    :param offset: int: The number of images to skip
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A list of image objects
    """
    images = await repository_pictures.get_images(limit, offset, current_user, db)
    if images is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return images


@router.get("/{image_id}", response_model=ImageModel, status_code=status.HTTP_200_OK)
async def get_image(image_id: int,
                    current_user: User = Depends(auth_service.get_current_user),
                    db: Session = Depends(get_db)):
    """
    The **get_image** function gets a single image from the database.

    :param image_id: int: The id of the image to return
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """
    image = await repository_pictures.get_image(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_image(image_id: int,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The **remove_image** function deletes a single image from the database.

    :param image_id: int: The id of the image to delete
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """
    image = await repository_pictures.remove(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image


@router.patch("/image_editor", response_model=ImageResponseEdited, status_code=status.HTTP_201_CREATED)
async def image_editor(image_id: int,
                       body: EditImageModel,
                       current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The **image_editor** function edits a single image from the database.

    :param image_id: int: The id of the image to edit
    :param body: EditImageModel: The body of the request
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """
    image = await repository_pictures.image_editor(image_id, body, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image


@router.patch("/description/{image_id}", response_model=ImageResponseUpdated)
async def edit_description(image_id: int,
                           description: str,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    """
    The **edit_description** function edits the description of a single image from the database.

    :param image_id: int: The id of the image to edit
    :param description: str: The description of the image
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """
    image = await repository_pictures.edit_description(image_id, description, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image


@router.post("/qr_code", status_code=status.HTTP_201_CREATED)
async def generate_qr_code(image_id: int,
                           current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    """
    The **generate_qr_code** function generates a QR code for a single image from the database.

    :param image_id: int: The id of the image to generate a QR code for
    :param current_user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    """
    image = await repository_pictures.qr_code_generator(image_id, current_user, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return image
