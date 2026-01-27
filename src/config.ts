
export const API_BASE_URL = import.meta.env.DEV
    ? 'http://localhost:8000'
    : '';

// In production, we assume the frontend is served from the same origin as the API (e.g. via FastAPI StaticFiles or Nginx reverse proxy).
// If served separately, this can be changed to the hardcoded backend URL.
