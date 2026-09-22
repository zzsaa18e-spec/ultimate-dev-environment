import os
import pytest
import psycopg2


@pytest.fixture(scope="session")
def db_url():
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("No DATABASE_URL configured — skipping DB tests")
    return url


@pytest.fixture
def db(db_url):
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    yield conn
    conn.close()
