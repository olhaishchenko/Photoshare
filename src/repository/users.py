from sqlalchemy.orm import Session

from src.database.models import User, Image
from src.schemas import UserModel, UpdateUser


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    Retrieves user specified by email

    :param email: email to search user by
    :type email: str
    :param db: The database session
    :type db: Session
    :return: Founded user
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


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
            "created_at": user.created_at}
