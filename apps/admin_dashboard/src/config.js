// API base URL is injected at build time via REACT_APP_API_BASE_URL env var.
// In docker-compose, set via the backend service's environment.
export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || '/api';
