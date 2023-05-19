import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User, Image
from src.repository.users import (
    update_user_info,
    get_user_info,
    ban_user
)
from src.schemas import UpdateUser


class TestUsersRepos(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email='user@email.com')

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
