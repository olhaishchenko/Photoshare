import hashlib
from uuid import uuid4

import cloudinary
import cloudinary.uploader

from src.config.config import settings
from src.schemas import ImageEditorModel



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


    @staticmethod
    def edit_image(image_url: str, body: ImageEditorModel):
        '''
        The **edit_image** function edits an image.
        It takes an image url and a body as input.
        The body contains the edit function and the width of the image.
        The edit function can be one of the following: resize, crop, fit, rotate.
        
        :param image_url: The url of the image
        :param body: The body of the request
        :return: The url of the edited image
        '''
        if body.edit_func == "resize":
            return CloudImage.resize_image(image_url, body.width, body.width)
        elif body.edit_func == "crop":
            return CloudImage.crop_image(image_url, body.width, body.width)
        elif body.edit_func == "fit":
            return CloudImage.fitted_image(image_url, body.width, body.width)
        elif body.edit_func == "rotate":
            return CloudImage.rotated_image(image_url, body.width)
        else:
            return image_url



    @staticmethod
    def resize_image(public_id: str, width: int, height: int):
        '''
        The **resize_image** function resizes an image.
        It takes an image url and a width and height as input.
        
        :param public_id: The name of the image
        :param width: The width of the image
        :param height: The height of the image
        :return: The url of the resized image
        '''
        resized_url = cloudinary.utils.cloudinary_url(public_id, width=width, height=height, crop="scale")
        return resized_url[0]
    

    @staticmethod
    def crop_image(public_id: str, width: int, height: int):
        '''
        The **crop_image** function crops an image.
        It takes an image url and a width and height as input.
        
        :param public_id: The name of the image
        :param width: The width of the image
        :param height: The height of the image
        :return: The url of the cropped image
        '''
        resized_url = cloudinary.utils.cloudinary_url(public_id, width=width, height=height, crop="crop")
        return resized_url[0]
    

    @staticmethod
    def fitted_image(public_id: str, width: int, height: int):
        '''
        The **fitted_image** function fits an image.
        It takes an image url and a width and height as input.
        
        :param public_id: The name of the image
        :param width: The width of the image
        :param height: The height of the image
        :return: The url of the fitted image
        '''
        resized_url = cloudinary.utils.cloudinary_url(public_id, width=width, height=height, crop="fit")
        return resized_url[0]
    

    # @staticmethod
    # def rotated_image(public_id: str, angle: int):
    #     resized_url = cloudinary.utils.cloudinary_url(public_id, angle=angle)
    #     return resized_url[0]
    

    