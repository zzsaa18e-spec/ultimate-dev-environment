-- Migration 004: service requests

CREATE TABLE IF NOT EXISTS service_requests (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id  UUID        NOT NULL REFERENCES users(id),
    provider_id  UUID        REFERENCES users(id),
    status       TEXT        NOT NULL DEFAULT 'pending'
                             CHECK (status IN ('pending','accepted','in_progress','completed','cancelled')),
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sr_customer ON service_requests(customer_id);
CREATE INDEX IF NOT EXISTS idx_sr_provider ON service_requests(provider_id);
