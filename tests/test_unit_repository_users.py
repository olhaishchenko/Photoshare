import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Image, Role
from src.repository.users import (
    update_user_info,
    get_user_info,
    ban_user,
    get_me,
    make_user_role, get_user_by_email, confirmed_email, update_avatar, get_users, remove_from_users
)
from src.schemas.users import UpdateUser


class TestUsersRepos(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email='user@email.com', username='boroda', is_active='True', roles = 'user', confirmed='False')
    async def test_get_me(self):
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await get_me(user, self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter_by().first.return_value = user
        response = await get_user_by_email(user.email, self.session)
        self.assertEqual(response, user)

    async def test_update_user_info_email(self):
        new_email = "test_email@email.com"
        body = UpdateUser(email=new_email)
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await update_user_info(user.email, body, self.session)
        self.assertEqual(result.email, new_email)

    async def test_update_user_info_username(self):
        new_username = "new_username"
        body = UpdateUser(username=new_username)
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await update_user_info(user.email, body, self.session)
        self.assertEqual(result.username, new_username)

    async def test_get_user_info(self):
        current_user = self.user
        self.session.query().filter().first.return_value = self.user
        self.session.query().filter().all.return_value = [Image, Image, Image]
        result = await get_user_info(current_user, self.session)
        print(result)
        self.assertEqual(result['images_count'], 3)

    async def test_ban_user_found(self):
        self.session.query().filter().first.return_value = self.user
        await ban_user(1, self.session)
        self.assertFalse(self.user.is_active)

    async def test_ban_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await ban_user(1, self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        user = self.user
        self.session.query().filter_by().first.return_value = user
        await confirmed_email(user.email, self.session)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        user = self.user
        self.session.query().filter_by().first.return_value = user
        url = "http://someurl.jpeg"
        result = await update_avatar(user.email, url, self.session)
        self.assertEqual(result.avatar, url)

    async def test_make_user_role(self):
        user = self.user
        role = 'admin'
        self.session.query().filter().first.return_value = user
        await make_user_role(user.email, role, self.session)
        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result.roles, 'admin')

    async def test_get_users(self):
        users = [User(), User(), User()]
        self.session.query().offset().limit().all.return_value = users
        result = await get_users(0, 10, self.session)
        self.assertEqual(result, users)

    async def test_remove_from_users(self):
        user = [User(id=1), User(), User()]
        self.session.query().filter().first.return_value = user
        result = await remove_from_users(1, self.session)
        self.assertEqual(result, user)

    async def test_remove_from_users_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_from_users(1, self.session)
        self.assertIsNone(result)

