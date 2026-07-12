import axios from 'axios';
import { useAuthStore } from '@/stores/auth.store';

/**
 * Use same-origin /api/v1 proxy (see next.config.ts rewrites).
 * Works for localhost:3000 AND LAN IP 192.168.x.x:3000 — no firewall/CORS issues.
 */
function resolveApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    return '/api/v1';
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
}

const api = axios.create({
  baseURL: resolveApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    config.baseURL = resolveApiBaseUrl();

    if (typeof window !== 'undefined') {
      // Read from Zustand memory first — localStorage may lag right after login
      const token = useAuthStore.getState().token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthRoute = error.config?.url?.includes('/auth/login')
      || error.config?.url?.includes('/auth/register');
    const url = error.config?.url || '';
    const isOptionalData = url.includes('/profile') || url.includes('/history');
    if (error.response?.status === 401 && !isAuthRoute && !isOptionalData) {
      if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
