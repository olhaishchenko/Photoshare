from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.database.models import User, Comment, Role
from src.schemas.comments import CommentBase


async def add_comment(image_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    """
    Adds a new comment to the database.

    :param image_id: int: Identify the image that the comment is being added to
    :param body: CommentBase: Specify the type of data that is expected to be passed in
    :param db: Session: Access the database
    :param user: User: Get the user_id from the logged-in user
    :return: A comment object
    """
    new_comment = Comment(comment=body.comment, image_id=image_id, user_id=user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


async def edit_comment(comment_id: int, body: CommentBase, db: Session, user: User) -> Comment | None:
    """
    Allows a user to edit their own comment.

    :param comment_id: int: Find the comment in the database
    :param body: CommentBase: Pass the data from the request body to this function
    :param db: Session: Connect to the database
    :param user: User: Check if the user is an admin, moderator or the author of the comment
    :return: A comment object
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if user.roles in [Role.admin, Role.moderator] or comment.user_id == user.id:
            comment.comment = body.comment
            comment.updated_at = func.now()
            db.commit()
    return comment


async def delete_comment(comment_id: int, db: Session, user: User) -> None:
    """
    Deletes a comment from the database. The comment can be deleted by Admin and Moderator

    :param comment_id: int: Identify the comment to be deleted
    :param db: Session: Connect to the database
    :param user: User: Check if the user is Admin or Moderator and authorized to delete a comment
    :return: The comment that was deleted
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        if user.roles in [Role.admin, Role.moderator]:
            db.delete(comment)
            db.commit()
    return comment


async def get_comment_by_id(comment_id: int, db: Session, user: User) -> Comment | None:
    """
    Returns a comment from the database by comment_id.

    :param comment_id: int: Specify the id of the comment that we want to retrieve
    :param db: Session: Access the database
    :param user: User: Check if the user is authorized to see comment
    :return: The comment with the given id, if it exists
    """
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def get_comments_by_user_id(user_id: int, db: Session) -> List[Comment] | None:
    """
    Returns a list of comments made by the user with the given id.
    If no such user exists, it returns None.

    :param user_id: int: Specify the user_id of the user whose comments we want to retrieve
    :param db: Session: Pass the database session to the function
    :return: A list of comments
    """
    return db.query(Comment).filter(Comment.user_id == user_id).all()


async def get_user_comments_by_image(user_id: int, image_id: int, db: Session) -> List[Comment] | None:
    """
    Returns a list of comments for a given user and image.

    :param user_id: int: Filter the comments by user_id
    :param image_id: int: Filter the comments by image_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments, or none if the user doesn't exist
    """
    return db.query(Comment).filter(and_(Comment.user_id == user_id, Comment.image_id == image_id)).all()


async def get_image_comments(image_id: int, db: Session) -> List[Comment]:
    """
    Returns a list of comments for the specified image_id.

    :param image_id: int: Filter the comments by image_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments for a given image
    """
    return db.query(Comment).filter(Comment.image_id == image_id).all()
