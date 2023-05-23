import sys
import os

from unittest.mock import MagicMock, patch
import pytest

sys.path.append(os.getcwd())
from src.database.models import User
from src.services.auth import auth_service



@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.confirmed_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_get_images_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not Found"


def test_get_images(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)


def test_get_image_by_id(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data


def test_get_image_by_id_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not Found"


def test_remove_image(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text


def test_repeat_delete_image(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Not Found"

