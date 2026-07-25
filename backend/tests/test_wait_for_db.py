import socket
from unittest.mock import patch
import pytest
from scripts.wait_for_db import wait_for_postgres


def test_wait_for_postgres_success():
    with patch("socket.create_connection") as mock_conn:
        mock_conn.return_value.__enter__.return_value = mock_conn
        mock_conn.return_value.__exit__.return_value = False
        result = wait_for_postgres("localhost", 5432, timeout=5)
        assert result is True
        mock_conn.assert_called_once_with(("localhost", 5432), timeout=1)


def test_wait_for_postgres_timeout():
    with patch("socket.create_connection", side_effect=socket.error("Connection refused")):
        with patch("time.sleep", return_value=None):
            with pytest.raises(SystemExit) as exc_info:
                wait_for_postgres("localhost", 5432, timeout=1)
            assert exc_info.value.code == 1
