"""Run SQL migrations with a PostgreSQL advisory lock.

The advisory lock prevents two simultaneously-starting containers from
applying migrations concurrently — the second one blocks until the first
finishes and releases the lock, then finds all migrations already applied.
"""
import glob
import hashlib
import os
import sys
import time

import psycopg2

# Stable constant unique to this application; never changes.
MIGRATION_ADVISORY_LOCK_ID = 7_389_241


def _get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def run_migrations() -> None:
    conn = _get_conn()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Block until we hold the advisory lock.
            cur.execute("SELECT pg_advisory_lock(%s)", (MIGRATION_ADVISORY_LOCK_ID,))

            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version    TEXT        PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    checksum   TEXT        NOT NULL
                )
            """)
            conn.commit()

            cur.execute("SELECT version FROM schema_migrations ORDER BY version")
            applied = {row[0] for row in cur.fetchall()}

            migration_dir = os.path.join(
                os.path.dirname(__file__), "../../db/migrations"
            )
            files = sorted(glob.glob(os.path.join(migration_dir, "*.sql")))

            for path in files:
                version = os.path.basename(path)
                if version in applied:
                    continue

                with open(path) as f:
                    sql = f.read()

                checksum = hashlib.sha256(sql.encode()).hexdigest()
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)",
                    (version, checksum),
                )
                conn.commit()
                print(f"[migrate] applied {version}", flush=True)

    except Exception:
        conn.rollback()
        raise
    finally:
        # Always release the lock, even on error.
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_advisory_unlock(%s)", (MIGRATION_ADVISORY_LOCK_ID,)
                )
                conn.commit()
        finally:
            conn.close()


if __name__ == "__main__":
    run_migrations()
