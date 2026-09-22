# ADR-001: Docker Compose Service Layout and Nginx Routing

**Status:** Accepted  
**Date:** 2026-09-22

## Context

The system consists of multiple front-end and back-end services that must
be exposed under a single origin for development and CI.

## Decision

- A single Nginx container is the only service with a host-bound port (`:80`).
- Traffic is routed by path prefix:
  - `/` → `request_web:80`
  - `/admin_dashboard/` → `admin_dashboard:80`
  - `/api/` → `backend:8000` (prefix stripped)
- PostgreSQL and the backend container expose **no host ports** in
  `docker-compose.yml` (production / CI).
- In `docker-compose.dev.yml` (development overlay), both are exposed on
  `127.0.0.1` only, preventing access from the LAN.
- Seed data is loaded exclusively via a volume mount in the dev overlay;
  it is never baked into images or loaded in production.

## Consequences

- Single entry point simplifies TLS termination (one cert, one listener).
- Developers can inspect Postgres directly on `localhost:5432` in dev
  without the port being reachable from other machines.
- The `/api/` path strip means the backend does not need to be aware of
  its deployment prefix.
