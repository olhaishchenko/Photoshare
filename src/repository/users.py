
from libgravatar import Gravatar



from sqlalchemy.orm import Session

from src.database.models import User, Image, Role
from src.schemas import UserModel, UpdateUser



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

#
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
    user.is_active = False
    db.commit()

    return {"id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "created_at": user.created_at}

