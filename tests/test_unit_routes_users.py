import unittest
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.config.detail import USER_BANNED, PRIVILEGES_DENIED
from src.database.models import User
from src.routes.users import ban_user
from src.services.auth import auth_service


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

    # @pytest.fixture
    # def token(client, user, session, monkeypatch):
    #     mock_send_email = MagicMock()
    #     monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    #     client.post("/api/auth/signup", json=user)
    #     current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    #     current_user.is_verify = True
    #     session.commit()
    #     response = client.post(
    #         "/api/auth/login",
    #         data={"username": user.get('email'), "password": user.get('password')},
    #         )
    #     data = response.json()
    #     return data["access_token"]
    #
    #
    # def test_get_me(client, token, monkeypatch):
    #     with patch.object(auth_service, 'redis_cache') as r_mock:
    #         r_mock.get.return_value = None
    #         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.redis', MagicMock())
    #         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.identifier', MagicMock())
    #         monkeypatch.setattr('fastapi_limiter.FastAPILimiter.http_callback', MagicMock())
    #         response = client.get(
    #             "/api/user/me/",
    #             headers={"Authorization": f"Bearer {token}"}
    #         )
    #         assert response.status_code == 200, response.text
    #         data = response.json()
    #         assert data["username"] == "boroda"
    #         assert data["email"] == "boroda@example.com"
    #         assert data["role"] == "Admin"
    #         assert data["avatar"] == "http://someurl.jpeg"
    #         assert data["is_active"] == "True"