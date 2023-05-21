from unittest.mock import patch
from src.database.db import get_db


def test_get_db_success(session, client):
    # Override DBSession in get_db
    with patch('src.database.db.DBSession', return_value=session):
        for db in get_db():
            assert db == session
