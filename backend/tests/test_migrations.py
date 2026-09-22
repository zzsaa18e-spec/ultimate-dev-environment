import pytest
import os
from unittest.mock import patch, MagicMock

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")


def test_advisory_lock_id_is_stable():
    from app.db.migrate import MIGRATION_ADVISORY_LOCK_ID
    assert MIGRATION_ADVISORY_LOCK_ID == 7_389_241, (
        "Advisory lock ID must never change — changing it could allow concurrent migrations"
    )


def test_advisory_lock_released_on_exception():
    """The advisory lock must always be released, even when a migration fails."""
    from app.db.migrate import run_migrations, MIGRATION_ADVISORY_LOCK_ID

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    # Simulate a migration failure after the lock is acquired
    execute_calls = []

    def fake_execute(sql, params=None):
        execute_calls.append(sql)
        if "CREATE TABLE" in sql:
            raise RuntimeError("simulated DB error")

    mock_cursor.execute.side_effect = fake_execute

    with patch("app.db.migrate._get_conn", return_value=mock_conn):
        with pytest.raises(RuntimeError, match="simulated DB error"):
            run_migrations()

    # Verify pg_advisory_unlock was called (in the finally block)
    unlock_calls = [
        c for c in execute_calls if "pg_advisory_unlock" in str(c)
    ]
    assert len(unlock_calls) >= 1, "Advisory lock was not released after exception"
