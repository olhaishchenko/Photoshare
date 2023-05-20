"""Модуль який відповідає за всі операції поа'язані з авторизацією користувача
Функціонал:
1. Хешування паролю
2. Звірення хешованого паролю з введенним
3. Створення access, email verification і refresh токенів
4. Декодування refresh токену
5. Отримання поточного юзера
6. Отримання email з токена підтвердження
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
import pickle
import redis

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from src.config import detail

from src.config.config import settings
from src.database.db import get_db

from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail.NOT_VALIDATE,
        headers={"WWW-Authenticate": "Bearer"},
    )
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    async def blocklist(self, token):
        payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        if payload.get("scope") == "access_token":
            email = payload.get("sub")
            if email is None:
                raise self.credentials_exception
            jti = payload.get("jti")
            if jti is None:
                raise self.credentials_exception
            self.r.set(jti, 'true')

    def is_blocklisted(self, jti):
        return self.r.exists(jti)

    def get_password_hash(self, password: str):
        """
        Takes a password as input and returns the hash of that password.

        :password: str: Receive the password that is being hashed
        :return: A hashed password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """
        Takes a plain-text password and hashed password as arguments.

        :plain_password: Pass in the password entered by the user
        :hashed_password: Compare the hashed password stored in the database with a new plain text password that
            is entered by a user
        :return: True if the password is correct
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :data: dict: Pass the data to be encoded
        :expires_delta: Optional[float]: Set the expiration time for the access token
        :return: A jwt token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        payload = {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        payload['jti'] = str(uuid.uuid4())
        to_encode.update(payload)
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

        :data: dict: Pass the user's data to be encoded
        :expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token that is encoded with the user's id, username and email
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    def required_auth_with_email(self, token: str = Depends(oauth2_scheme)):
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise self.credentials_exception
                jti = payload.get("jti")
                if jti is None:
                    raise self.credentials_exception
                if self.is_blocklisted(jti):
                    raise self.credentials_exception
                return email
            else:
                raise self.credentials_exception
        except JWTError as e:
            raise self.credentials_exception

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Function is a dependency that will be used in the UserRouter class.
        It takes in a token and db session, and returns the user associated with that token.
        If no user is found, it raises an exception.

        :token: str: Pass the token to the function
        :db: Session: Get the database session
        :return: The user that is currently logged in
        """
        email = self.required_auth_with_email(token)

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise self.credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        if user is None:
            raise self.credentials_exception
        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode the refresh token.
        It takes a refresh_token as an argument and returns the email of the user if it's valid.
        If not, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail 'Could not validate credentials'.

        :refresh_token: str: Pass the refresh token to the function
        :return: The email of the user who is trying to refresh their access token
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail.INVALID_TOKEN)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail.NOT_VALIDATE)

    def create_email_token(self, data: dict):
        """
        Takes a dictionary of data and returns a token.
        The token is encoded with the SECRET_KEY, which is stored in the .env file.
        The algorithm used to encode the token is also stored in the .env file.

        :data: dict: Pass in the data to be encoded
        :return: A token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
        Takes a token as an argument and returns the email associated with that token.
        It does this by decoding the JWT using our SECRET_KEY and ALGORITHM, then checking to make sure that
        it has a scope of 'email_token'.
        If it does, we return the email from its payload. If not, we raise an HTTPException
        with status code 401 (Unauthorized) and detail message 'Invalid scope for token'.
        If there is any other error in decoding or validating the JWT (such as if it's expired),
        we raise an HTTPException with status code 422 (Unprocessable entity) and
        detail message 'Invalid token for email verification'.

        :token: str: Pass in the token that is sent to the user's email
        :return: The email from the token
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail.INVALID_TOKEN)

        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail.INVALID_TOKEN_EMAIL)


auth_service = Auth()
