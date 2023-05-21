from unittest.mock import patch

from fastapi import status

def test_healthchecker_successful(client, session):
    with patch('main.get_db', return_value=session):
        response = client.get("/api/healthchecker")
        assert response.status_code == status.HTTP_200_OK, response.text