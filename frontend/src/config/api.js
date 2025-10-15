import axios from 'axios';

// Smart base URL resolver: no manual toggling needed.
// Priority:
// 1) Explicit VITE_API_BASE_URL (hard override)
// 2) If running on localhost -> use local backend
// 3) Otherwise -> use production backend (VITE_API_BASE_URL_PROD or a sane default)

const DEFAULT_LOCAL = 'http://localhost:8000';
const DEFAULT_PROD = 'https://smart-resume-screener-jee0.onrender.com';

const ENV_BASE = (import.meta.env.VITE_API_BASE_URL || '').trim();
const ENV_PROD = (import.meta.env.VITE_API_BASE_URL_PROD || '').trim();

function resolveApiBaseUrl() {
  // 1) Hard override via env
  if (ENV_BASE) return ENV_BASE;

  // 2) Infer from window location
  try {
    if (typeof window !== 'undefined') {
      const host = window.location.hostname;
      const isLocal = host === 'localhost' || host === '127.0.0.1';
      return isLocal ? DEFAULT_LOCAL : (ENV_PROD || DEFAULT_PROD);
    }
  } catch (_) {
    // no-op
  }

  // 3) Fallback to production default in non-browser contexts
  return ENV_PROD || DEFAULT_PROD;
}

const API_BASE_URL = resolveApiBaseUrl();

// Create an axios instance with the resolved base URL
const api = axios.create({ baseURL: API_BASE_URL });

if (typeof window !== 'undefined') {
  // Helpful one-liner for debugging which base URL is used
  // eslint-disable-next-line no-console
  console.info(`[SRS] API base URL => ${API_BASE_URL}`);
}

export default api;
export { API_BASE_URL };