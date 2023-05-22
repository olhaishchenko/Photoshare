from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.database.models import User, Image
from src.schemas.pictures import EditImageModel
from src.services.cloud_image import CloudImage
import cloudinary
import pyqrcode
import qrcode





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


async def image_editor(image_id: int, 
                       body: EditImageModel,
                       user: User,
                       db: Session):
    '''
    The **image_editor** function edits a single image from the database.
    
    :param image_id: int: The id of the image to edit
    :param body: EditImageModel: The body of the request
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await get_image_from_id(image_id, user, db)
    if image:
        edit_data = []
        if body.circle.use_filter and body.circle.height and body.circle.width:
            trans_list = [{'gravity': "face", 'height': f"{body.circle.height}", 'width': f"{body.circle.width}", 'crop': "thumb"},
            {'radius': "max"}]
            [edit_data.append(elem) for elem in trans_list]

        if body.effect.use_filter:
            effect = ""
            if body.effect.art_audrey:
                effect = "art:audrey"
            if body.effect.art_zorro:
                effect = "art:zorro"
            if body.effect.blur:
                effect = "blur:300"
            if body.effect.cartoonify:
                effect = "cartoonify"
            if effect:
                edit_data.append({"effect": f"{effect}"})

        if body.resize.use_filter and body.resize.height and body.resize.height:
            crop = ""
            if body.resize.crop:
                crop = "crop"
            if body.resize.fill:
                crop = "fill"
            if crop:
                trans_list = [{"gravity": "auto", 'height': f"{body.resize.height}", 'width': f"{body.resize.width}", 'crop': f"{crop}"}]
                [edit_data.append(elem) for elem in trans_list]

        if body.rotate.use_filter and body.rotate.width and body.rotate.degree:
            trans_list = [{'width': f"{body.rotate.width}", 'crop': "scale"}, {'angle': "vflip"}, {'angle': f"{body.rotate.degree}"}]
            [edit_data.append(elem) for elem in trans_list]

        if edit_data:
            CloudImage()
            uri = cloudinary.CloudinaryImage(image.image_url).build_url(transformation=edit_data)
            image.image_url = uri
            print(uri)
            db.commit()
            db.refresh(image)
            return image


async def edit_description(image_id: int, 
                           description: str,
                           user: User,
                           db: Session):
    '''
    The **edit_description** function edits a single image from the database.
    
    :param image_id: int: The id of the image to edit
    :param body: EditDescriptionModel: The body of the request
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await get_image_from_id(image_id, user, db)
    if image:
        image.description = description
        db.commit()
        db.refresh(image)
        return image
    

async def qr_code_generator(image_id: int, 
                            user: User,
                            db: Session):
    '''
    The **qr_code_generator** function edits a single image from the database.
    
    :param image_id: int: The id of the image to edit
    :param user: User: The user object
    :param db: Session: A connection to our Postgres SQL database.
    :return: A image object
    '''
    image = await get_image_from_id(image_id, user, db)
    if image:
        image_url = image.image_url
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(image_url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(f"qr_code_{image_id}.png")
        return f"qr_code_{image_id}.png"
    

