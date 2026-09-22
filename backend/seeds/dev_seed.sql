-- DEV-ONLY seed data — loaded via docker-compose.dev.yml volume mount.
-- This file is NEVER loaded in production.
-- Provides predictable test users for local development.

INSERT INTO users (id, phone, role) VALUES
    ('00000000-0000-0000-0000-000000000001', '+966500000001', 'customer'),
    ('00000000-0000-0000-0000-000000000002', '+966500000002', 'provider'),
    ('00000000-0000-0000-0000-000000000003', '+966500000003', 'admin')
ON CONFLICT (phone) DO NOTHING;

INSERT INTO provider_profiles (user_id, display_name, bio, verified) VALUES
    ('00000000-0000-0000-0000-000000000002', 'Test Provider', 'Dev seed provider', TRUE)
ON CONFLICT (user_id) DO NOTHING;
