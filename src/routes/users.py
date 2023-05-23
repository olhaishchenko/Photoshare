from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config import detail
from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.users import UserDb, UpdateUser, UserInfoResponse, UserBanned, RequestRole
from src.schemas.pictures import ImageModel
from src.services.auth import auth_service
from src.services.roles import CheckRole
from src.repository import users as repository_users

user_router = APIRouter(prefix="/user", tags=['users'])

security = HTTPBearer()

allowed_all_user = CheckRole([Role.admin, Role.moderator, Role.user])
allowed_get_all_users = CheckRole([Role.admin])
allowed_remove_user = CheckRole([Role.admin, Role.moderator])
allowed_ban_user = CheckRole([Role.admin])
allowed_change_user_role = CheckRole([Role.admin])


@user_router.get("/me", response_model=UserDb, dependencies=[Depends(allowed_all_user)])
async def read_users_me(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The **read_users_me** function is a GET endpoint that returns the current user's information.
    It uses the auth_service to get the current user, and then returns it.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    user = await repository_users.get_me(current_user, db)
    return user


@user_router.patch('/me/', response_model=UserDb, dependencies=[Depends(allowed_all_user)])
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


@user_router.delete('/{user_id}', dependencies=[Depends(allowed_remove_user)])
async def user_remove(user_id, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Ban user

    :param current_user: user whose info is changing
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: banned user info with message of success
    :rtype: dict
    """
    await repository_users.remove_from_users(user_id, db)
    return {"user_id": user_id, "detail": detail.USER_REMOVE}


@user_router.get('/info/', response_model=UserInfoResponse, dependencies=[Depends(allowed_all_user)])
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


@user_router.put('/ban/{id_}/', response_model=UserBanned, dependencies=[Depends(allowed_ban_user)])
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
    print('current user role', str(current_user.roles))
    if str(current_user.roles) != "Role.admin":
        raise HTTPException(status_code=403, detail=detail.PRIVILEGES_DENIED)
    banned_user = await repository_users.ban_user(id_, db)
    return {"user": banned_user, "detail": detail.USER_BANNED}


@user_router.get("/all/", response_model=List[UserDb], dependencies=[Depends(allowed_get_all_users)])
async def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    The **read_all_users** function returns a list of users.
        ---
        get:
          summary: Returns all users.
          description: This can only be done by the logged in user.
          operationId: read_all_users
          parameters:
            - name: skip (optional)  # The number of records to skip before returning results, default is 0 (no records skipped).  Used for pagination purposes.   See https://docs.mongodb.com/manual/reference/method/cursor.skip/#cursor-skip-examples for more information on how this

    :param skip: int: Skip the first n records
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database connection to the function
    :return: A list of users
    """
    users = await repository_users.get_users(skip, limit, db)
    return users


@user_router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db)):
    """
    The **make_role_by_email** function is used to change the role of a user.
        The function takes in an email and a role, and changes the user's role to that specified by the inputted
        parameters. If no such user exists, then an HTTPException is raised with status code 401 (Unauthorized)
        and detail message &quot;Invalid Email&quot;. If the new role matches that of the current one, then a message saying so
        will be returned. Otherwise, if all goes well, then a success message will be returned.

    :param body: RequestRole: Get the email and role from the request body
    :param db: Session: Access the database
    :return: A dictionary with a message key
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail.INVALID_EMAIL)
    if body.roles == user.roles:
        return {"message": detail.USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.roles, db)
        return {"message": f"{detail.USER_CHANGE_ROLE_TO} {body.roles.value}"}


@user_router.get("/commented_images_by_me/", response_model=List[ImageModel])
async def read_commented_images_by_me(db: Session = Depends(get_db),
                                     current_user: User = Depends(auth_service.get_current_user)):
    """
    The **read_commented_images_by_me** function returns all images that the current user has commented on.

    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A list of images that the user has commented on
    """
    images = await repository_users.get_all_commented_images(current_user, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.NOT_FOUND)
    return images


@user_router.get("/rated_images_by_me/", response_model=List[ImageModel])
async def read_liked_images_by_me(db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    """
    The **read_liked_images_by_me** function returns all images liked by the current user.
        The function is called when a GET request is made to the /users/me/liked_images endpoint.

    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user object of the current logged in user
    :return: A list of images that the user liked
    """
    images = await repository_users.get_all_liked_images(current_user, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.NOT_FOUND)
    return images
