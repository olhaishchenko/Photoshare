from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User, Role
from src.schemas import UserModel


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