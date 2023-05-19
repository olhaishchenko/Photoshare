import unittest
from fastapi import HTTPException
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.config.detail import USER_BANNED, PRIVILEGES_DENIED
from src.database.models import User
from src.routes.users import ban_user


class TestUsersRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User()
        self.current_user = User(roles='Role.admin')

    async def test_ban_user_admin(self):
        self.session.query().filter().first.return_value = self.user
        result = await ban_user(1, self.session, self.current_user)
        self.assertEqual(result['detail'], USER_BANNED)

    async def test_ban_user_not_admin(self):
        self.session.query().filter().first.return_value = self.user
        self.current_user.roles = 'Role.user'
        with self.assertRaises(HTTPException) as context:
            await ban_user(1, self.session, self.current_user)
        self.assertEqual(403, context.exception.status_code)
