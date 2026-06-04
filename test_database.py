import pytest
from unittest.mock import patch, MagicMock
from database import get_db

def test_get_db_success():
    """Test that get_db yields a session and closes it correctly on normal completion."""
    with patch('database.SessionLocal') as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()

        # Generator yields the db instance
        db = next(gen)
        assert db == mock_db
        mock_db.close.assert_not_called()

        # Resuming generator completes it, calling close() in finally block
        with pytest.raises(StopIteration):
            next(gen)

        mock_db.close.assert_called_once()

def test_get_db_exception_handling():
    """Test that get_db closes the session even if an exception occurs during iteration."""
    with patch('database.SessionLocal') as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        gen = get_db()

        # Generator yields the db instance
        db = next(gen)
        assert db == mock_db
        mock_db.close.assert_not_called()

        # Inject an exception into the generator to simulate error in endpoint
        with pytest.raises(ValueError, match="Database operation failed"):
            gen.throw(ValueError("Database operation failed"))

        # Verify finally block still executed
        mock_db.close.assert_called_once()
