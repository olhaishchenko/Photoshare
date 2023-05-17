from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.database.models import User, Image



async def create(description: str, image_url: str, user: User, db: Session):
    '''
    The **create** function creates a new image in the database.

    :param description: str: The description of the image
    :param image_url: str: The url of the image
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = Image(description=description, image_url=image_url, user_id=user.id)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def get_images(limit: int, offset: int, user: User, db: Session):
    '''
    The **get_images** function gets all the images from the database.
    
    :param limit: int: The number of images to return
    :param offset: int: The number of images to skip
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A list of image objects
    '''
    images = db.query(Image).filter(and_(Image.user_id == user.id)).\
        order_by(desc(Image.created_at)).limit(limit).offset(offset).all()
    return images


async def get_image(image_id: int, user: User, db: Session):
    '''
    The **get_image** function gets a single image from the database.
    
    :param image_id: int: The id of the image to return
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = db.query(Image).filter(and_(Image.user_id == user.id, Image.id == image_id)).\
        order_by(desc(Image.created_at)).first()
    return image


async def get_image_from_id(image_id: int, user: User, db: Session):
    '''
    The **get_image_from_id** function gets a single image from the database.
    
    :param image_id: int: The id of the image to return
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = db.query(Image).filter(and_(Image.id == image_id, Image.user_id == user.id)).first()
    return image


async def get_image_from_url(image_url: str, user: User, db: Session):
    '''
    The **get_image_from_url** function gets a single image from the database.
    
    :param image_url: str: The url of the image to return
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = db.query(Image).filter(and_(Image.image_url == image_url, Image.user_id == user.id)).first()
    return image


async def remove(image_id: int, user: User, db: Session):
    '''
    The **remove** function deletes a single image from the database.
        
    :param image_id: int: The id of the image to delete
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await get_image_from_id(image_id, user, db)
    db.delete(image)
    db.commit()
    return image