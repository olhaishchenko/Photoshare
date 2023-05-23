from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.schemas.comments import CommentBase, CommentUpdate, CommentModel
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.config import detail
from src.services.roles import CheckRole
from src.database.models import User, Role

router = APIRouter(prefix='/comments', tags=["comments"])

allowed_get_comments = CheckRole([Role.admin, Role.moderator, Role.user])
allowed_add_comments = CheckRole([Role.admin, Role.moderator, Role.user])
allowed_edit_comments = CheckRole([Role.admin, Role.moderator, Role.user])
allowed_delete_comments = CheckRole([Role.admin, Role.moderator])


@router.post("/{image_id}",
             response_model=CommentModel,
             dependencies=[Depends(allowed_add_comments)])
async def add_comment(image_id: int, body: CommentBase, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new comment for the image with the given id.

    :param image_id: int: Specify the image that the comment is being created for
    :param body: CommentBase: Pass the data from the request body to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A comment object, which is then serialized as json
    """
    new_comment = await repository_comments.add_comment(image_id, body, db, current_user)
    return new_comment


@router.put("/{comment_id}",
            response_model=CommentUpdate,
            dependencies=[Depends(allowed_edit_comments)])
async def edit_comment(comment_id: int, body: CommentBase, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Allows a user to edit their own comment.

    :param comment_id: int: Identify the comment to be edited
    :param body: CommentBase: Pass the comment body to the edit_comment function
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged-in
    :return: None, but the function expects a CommentBase object
    """
    edited_comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if edited_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.COMMENT_NOT_FOUND)
    return edited_comment


@router.delete("/{comment_id}",
               response_model=CommentModel,
               dependencies=[Depends(allowed_delete_comments)])
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a specified comment from the database.

    :param comment_id: int: Specify the comment that is to be deleted
    :param db: Session: Get the database session from the dependency
    :param current_user: User: Check if the user is logged-in
    :return: The deleted comment
    """
    deleted_comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if deleted_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.COMMENT_NOT_FOUND)
    return deleted_comment


@router.get("/{comment_id}",
            response_model=CommentModel,
            dependencies=[Depends(allowed_get_comments)])
async def get_comments(comment_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns a specified comment from the database.

    :param comment_id: int: Pass the comment id to the function
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The comment object, but i want to return the comment_id
    """
    comment = await repository_comments.get_comment_by_id(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.COMMENT_NOT_FOUND)
    return comment


@router.get("/author/{user_id}",
            response_model=List[CommentModel],
            dependencies=[Depends(allowed_get_comments)])
async def all_user_comments(user_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns all comments made by a user.

    :param user_id: int: Specify the user_id of the user whose comments we want to see
    :param db: Session: Pass the database session to the function
    :param current_user: User: Check if the user is logged-in
    :return: A list of comments
    """
    comments = await repository_comments.get_comments_by_user_id(user_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.COMMENT_NOT_FOUND)
    return comments


@router.get("/image_by_author/{user_id}/{image_id}",
            response_model=List[CommentModel],
            dependencies=[Depends(allowed_get_comments)])
async def user_comments_for_image(user_id: int, image_id: int, db: Session = Depends(get_db),
                                  current_user: User = Depends(auth_service.get_current_user)):
    """
    Returns all comments for a given user and image.

    :param user_id: int: Specify the user_id of the user whose comments we want to retrieve
    :param image_id: int: Get the comments for a specific image
    :param db: Session: Access the database
    :param current_user: User: Get the current user who is logged-in
    :return: A list of comments that belong to a image
    """
    comments = await repository_comments.get_user_comments_by_image(user_id, image_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail.COMMENT_NOT_FOUND)
    return comments
