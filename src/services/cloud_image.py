import hashlib
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from src.config.config import settings


class CloudImage:
    '''
    The **CloudImage** class is a wrapper around the Cloudinary API.
    It provides methods to upload, edit and delete images.
    
    :param cloud_name: str: The name of the cloudinary account
    :param api_key: str: The api key of the cloudinary account
    :param api_secret: str: The api secret of the cloudinary account
    :param secure: bool: Whether to use https or not
    '''
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_image():
        '''
        The **generate_name_image** function generates a random name for the image.
        It uses the uuid4 function to generate a random string and then hashes it using sha256.
        
        :return: A random string
        '''
        name = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest()
        return f"photo_share/{name}"

    @staticmethod
    def upload(file, public_id: str, overwrite=True):
        '''
        The **upload** function uploads an image to Cloudinary.
        
        :param file: The image file
        :param public_id: The name of the image
        :param overwrite: Whether to overwrite the image or not
        :return: The response from Cloudinary
        '''
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=overwrite)
        return r
    
    @staticmethod
    def get_url_for_image(file_name):
        '''
        The **get_url_for_image** function gets the url for an image.
        
        :param file_name: The name of the image
        :return: The url of the image
        '''
        src_url = cloudinary.utils.cloudinary_url(file_name)
        return src_url[0]
    

        