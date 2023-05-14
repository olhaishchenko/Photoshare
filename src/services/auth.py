"""Модуль який відповідає за всі операції поа'язані з авторизацією користувача
Функціонал:
1. Хешування паролю
2. Звірення хешованого паролю з введенним
3. Створення access, email verification і refresh токенів
4. Декодування refresh токену
5. Отримання поточного юзера
6. Отримання email з токена підтвердження
"""
#
from datetime import datetime, timedelta
from typing import Optional
import pickle
import redis

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.config.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pass

auth_service = Auth()
