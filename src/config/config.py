from pydantic import BaseSettings


class Settings(BaseSettings):

    sqlalchemy_database_url: str = 'postgresql+psycopg2://postgres:1234@localhost:5432/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    mail_username: str = 'volodymyr.oliinyk@meta.ua'
    mail_password: str = 'ReptilesOwnUs16'
    mail_from: str = 'volodymyr.oliinyk@meta.ua'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'dvrbkvnto'
    cloudinary_api_key: int = 661881531523377
    cloudinary_api_secret: str = 'VFzARWdPhgyAHcBLntfBpemyuHk'

    class Config:
        case_sensitive = True
        env_file = "../../.env"
        env_file_encoding = "utf-8"


settings = Settings()
