from datetime import datetime

import pytest

from src.database.models import User, Comment, Image
from src.schemas.comments import CommentBase
from src.repository import comments as repository_comments


@pytest.fixture()
def new_user(user, session):
    """
    Takes a user object and a session object as arguments.
    It then queries the database for an existing user with the same email address.
    If no such user exists, it creates one using the information provided in 
    the argument 'user' and adds it to the database.
    
    :param user: Get the email, username and password from the user
    :param session: Access the database
    :return: A user object
    """
    new_user = session.query(User).filter(User.email == user.get('email')).first()
    if new_user is None:
        new_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user


@pytest.fixture()
def new_image(session):
    """
    Creates a new image in the database.
    
    :param session: Make a connection to the database
    :return: An object
    """
    image = Image(
        id=1,
        image_url="Column(String(255))",
        user_id=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description="Column(String(255)"
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


@pytest.fixture()
def comment(session):
    """
    Creates a comment object and adds it to the database.

    :param session: Pass the database session to the function
    :return: A comment object, which is then passed to the test_comment function
    """
    comment = Comment(
        id=1,
        comment="test_comment",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=1,
        image_id=1
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@pytest.mark.asyncio
async def test_add_comment(image, new_user, session):
    """
    Tests the add_comment function in repository_comments.py
    It adds a comment object and passes it to the add_comment function along with a session,
    user id, and image id. The response is then checked to make sure that it has been created correctly.
    
    :param image: Create a new image
    :param new_user: Create a new user in the database
    :param session: Pass the database session to the repository layer
    :return: A response with the comment - test_comment, user_id - 1 and image_id - 1
    """
    comment = CommentBase(
        comment="test_comment",
    )
    response = await repository_comments.add_comment(1, comment, session, new_user)
    assert response.comment == "test_comment"
    assert response.user_id == 1
    assert response.image_id == 1
    
    
@pytest.mark.asyncio
async def test_edit_comment(new_user, session):
    """
    Tests the edit_comment function in repository_comments.py
    The test passes if the response is a CommentBase object with comment - new_comment
    
    :param new_user: Create a new user to be used in the test
    :param session: Create a new session for the test to run in
    :return: new_comment
    """
    new_comment = CommentBase(
        comment="new_comment",
    )
    response = await repository_comments.edit_comment(1, new_comment, session, new_user)
    assert response.comment == "new_comment"
    
    
@pytest.mark.asyncio
async def test_delete_comment(new_user, session):
    """
    Tests the delete_comment function in repository_comments.py
    The test passes if the response text is equal to new_comment
    
    :param new_user: Create a new user in the database
    :param session: Pass the session object to the function
    :return: new_comment
    """
    response = await repository_comments.delete_comment(1,  session, new_user)
    assert response.comment == "new_comment"
    
    
@pytest.mark.asyncio
async def test_get_comment_by_id(comment, new_user, session):
    """
    Tests the get_comment_by_id function in repository_comments.py
    by asserting that the response text is equal to test_comment.
    
    :param comment: Pass the comment fixture into the function
    :param new_user: Create a new user for the test
    :param session: Pass a database session to the function
    :return: A response object, but the function it's testing returns a string
    """
    response = await repository_comments.get_comment_by_id(1, session, new_user)
    assert response.comment == "test_comment"
    
    
@pytest.mark.asyncio
async def test_get_comments_by_user_id(new_user, session):
    """
    Tests the get_comments_by_user_id function in repository_comments.py
    It does this by creating a new user and then calling the get_comments_by_user_id function with that user's id.
    The response is checked to make sure it is a list, and that the first item in the list has an id of 1.
    
    :param new_user: Create a new user in the database
    :param session: Pass the database session to the repository function
    :return: A list of comments for a user with id 1
    """
    response = await repository_comments.get_comments_by_user_id(1, session)
    assert isinstance(response, list)
    assert response[0].user_id == 1
    
    
@pytest.mark.asyncio
async def test_get_user_comments_by_image(new_user, session):
    """
    Tests the get_user_comments_by_image function in the repository.py file.
    The test is successful if it returns a list of comments that belong to a specific user and image.
    
    :param new_user: Create a new user
    :param session: Pass the database session to the repository function
    :return: A list of comments for a specific user and image
    """
    response = await repository_comments.get_user_comments_by_image(1, 1, session)
    assert isinstance(response, list)
    assert response[0].user_id == 1
