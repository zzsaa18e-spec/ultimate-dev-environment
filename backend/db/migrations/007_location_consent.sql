-- Migration 007: location consent tracking
--
-- Tracks whether a user has granted permission for the app to access
-- their device location. Required by app-store policies and GDPR.
-- The E2E test fix for location consent updated only the test helper
-- (test code, not product code) to wait for the consent dialog before
-- proceeding — no product schema change was needed beyond this table.

CREATE TABLE IF NOT EXISTS location_consents (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    granted      BOOLEAN     NOT NULL,
    app_version  TEXT        NOT NULL,
    granted_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at   TIMESTAMPTZ
);

-- One active consent record per user (revoked ones kept for audit)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lc_user_active
    ON location_consents(user_id)
    WHERE revoked_at IS NULL;
