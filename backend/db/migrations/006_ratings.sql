-- Migration 006: ratings and reviews

CREATE TABLE IF NOT EXISTS ratings (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id  UUID        NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    rater_id    UUID        NOT NULL REFERENCES users(id),
    ratee_id    UUID        NOT NULL REFERENCES users(id),
    score       SMALLINT    NOT NULL CHECK (score BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
