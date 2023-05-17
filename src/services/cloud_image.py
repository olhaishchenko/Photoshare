import hashlib
from uuid import uuid4

import cloudinary
import cloudinary.uploader

from src.config.config import settings



class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_image():
        name = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest()
        return f"photo_share/{name}"

    @staticmethod
    def upload(file, public_id: str, overwrite=True):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=overwrite)
        return r
    
    @staticmethod
    def get_url_for_image(file_name):
        src_url = cloudinary.utils.cloudinary_url(file_name)
        return src_url[0]