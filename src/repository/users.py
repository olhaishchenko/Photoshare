from typing import List

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User, Image, Role, Comment
from src.schemas.users import UserModel, UpdateUser


async def get_me(user: User, db: Session) -> User:
    """
    The **get_me** function returns the user object of the current logged in user.


    :param user: User: Get the user id
    :param db: Session: Access the database
    :return: A user object
    """
    user = db.query(User).filter(User.id == user.id).first()
    return user


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The **get_user_by_emai** function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Filter the database for a user with that email
    :param db: Session: Pass the database session to the function
    :return: A user object if the email is found in the database,
    """
    user = db.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, db: Session):
    """
    The **create_user** function creates a new user in the database.

    :param body: UserModel: Validate the data that is passed in
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    g = Gravatar(body.email)

    new_user = User(**body.dict(), avatar=g.get_image())
    if len(db.query(User).all()) == 0:  # First user always admin
        new_user.roles = Role.admin
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The **update_token** function updates the refresh token for a user in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token to store in the database.
            db (Session): A connection to our Postgres SQL database.

    :param user: User: Pass the user object to the function
    :param refresh_token: Get a new access token from the spotify api
    :param db: Session: Pass a database session to the function
    :return: The user's refresh token
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The **confirmed_email** function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to the function
    :return: Nothing
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The **update_avatar** function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_user_info(email, body: UpdateUser, db: Session):
    """
    Change user name or email. Empty fields stay the same.

    :param email: email to search user by
    :type email: str
    :param body: new data
    :type body: UpdateUser
    :param db: The database session
    :type db: Session
    :return: updated user
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.username = body.username if body.username else user.username
    user.email = body.email if body.email else user.email
    db.commit()

    return user


# async def create_one_user(body: UserModel, db: Session):
#     new_user = User(**body.dict())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


# async def get_one_user(id_, db: Session):
#     return db.query(User).filter(User.id == id_).first()


async def get_user_info(current_user, db):
    """
    Get username of current user, when he join and number of images he have

    :param current_user: user whose info is extracting
    :type current_user: User
    :param db: The database session
    :type db: Session
    :return: user info
    :rtype: dict
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    images_count = len(db.query(Image).filter(Image.user_id == current_user.id).all())

    return {
        "username": user.username,
        "created_at": user.created_at,
        "images_count": images_count
    }


async def ban_user(id_, db: Session):
    """
    Make user's account inactive by id (for admins only)

    :param id_: id of user to ban
    :type id_: int
    :param db: The database session
    :type db: Session
    :return: banned user info
    :rtype: dict

    """
    user = db.query(User).filter(User.id == id_).first()
    if user:
        user.is_active = False
        db.commit()
        return {"id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar,
                "created_at": user.created_at}
    else:
        return None


async def make_user_role(email: str, role: Role, db: Session) -> None:

    """
    The **make_user_role** function takes in an email and a role, and then updates the user's role to that new one.
    Args:
    email (str): The user's email address.
    role (Role): The new Role for the user.

    :param email: str: Get the user by email
    :param role: Role: Set the role of the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.roles = role
    db.commit()


async def get_users(skip: int, limit: int, db: Session) -> List[User]:
    """
    The **get_users** function returns a list of users from the database.

    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    return db.query(User).offset(skip).limit(limit).all()


# async def get_all_liked_images(user: User, db: Session):
#     """
#     The **get_all_liked_images** function returns all images that a user has liked.
#         Args:
#             user (User): The User object to get the liked images for.
#             db (Session): A database session to use for querying the database.
#         Returns:
#             List[Image]: A list of Image objects that have been liked by the specified User.
#
#     :param user: User: Get the user's id
#     :param db: Session: Pass the database session to the function
#     :return: A list of images that the user liked
#     """
#     pass
#     # return db.query(Image).join(Rating).filter(Rating.user_id == user.id).all()


async def get_all_commented_images(user: User, db: Session):
    """
    The **get_all_commented_images** function returns all posts that a user has commented on.

    :param user: User: Get the user object from the database
    :param db: Session: Pass the database session to the function
    :return: All images that have been commented on by a user
    """
    return db.query(Image).join(Comment).filter(Comment.user_id == user.id).all()


async def remove_from_users(id_: int, db: Session) -> None:
    """
    The **remove_from_blacklist** function removes a user

    :param id_: int: id of user to remove
    :param db: Session: Access the database
    :return: None
    """
    user = db.query(User).filter(User.id == id_).first()
    print(user)
    if user:
        db.delete(user)
        db.commit()
    return user


