from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from src.config.detail import USER_BANNED, PRIVILEGES_DENIED
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserDb, UpdateUser, UserModel, UserResponse, UserInfoResponse, UserBanned
from src.services.auth import auth_service

from src.repository import users as repository_users

user_router = APIRouter(prefix="/user", tags=['users'])

security = HTTPBearer()

# @user_router.post('/create_test', response_model=UserResponse)
# async def create_one_user(body: UserModel, db: Session = Depends(get_db)):
#     exist_user = await repository_users.get_user_by_email(body.email, db)
#     if exist_user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
#     new_user = await repository_users.create_one_user(body, db)
#     return {"user": new_user, "detail": "User successfully created"}


@user_router.put('/edit', response_model=UserDb)
async def update_user_info(body: UpdateUser, current_user: User = Depends(auth_service.get_current_user),
                           db: Session = Depends(get_db)):
    """
    Edit information of user

    :param body: new data
    :type body: UpdateUser
    :param current_user: user whose info is changing
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: updated user
    :rtype: User
    """

    user = await repository_users.update_user_info(email=current_user.email, body=body, db=db)
    return user


@user_router.get('/info', response_model=UserInfoResponse)
async def user_info(db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    Get user info

    :param current_user: user whose info is changing
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: user info
    :rtype: dict

    """
    user_info = await repository_users.get_user_info(current_user, db)
    return user_info


@user_router.get('/ban/{id_}', response_model=UserBanned)
async def ban_user(id_, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Ban user

    :param current_user: user whose info is changing
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: banned user info with message of success
    :rtype: dict
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail=PRIVILEGES_DENIED)
    banned_user = await repository_users.ban_user(id_, db)
    return {"user": banned_user, "detail": USER_BANNED}
