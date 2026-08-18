import axios from "axios";
import { jwtDecode } from "jwt-decode";

export const API_BASE = process.env.DJANGO_API_URL || "http://localhost:8000";

// Create a server-side API client (no localStorage)
export const serverApi = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true
});

// Create a client-side API client (with localStorage support)
export const clientApi = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Client-side request interceptor (only runs in browser)
if (typeof window !== 'undefined') {
  clientApi.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem("access");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for token refresh
  let isRefreshing = false;
  let failedQueue: any[] = [];

  const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });
    failedQueue = [];
  };

  clientApi.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // If unauthorized and not already retrying
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return clientApi(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const refreshToken = localStorage.getItem("refresh");
          if (!refreshToken) {
            throw new Error("No refresh token");
          }

          const response = await axios.post(`${API_BASE}/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem("access", access);

          // Process queue
          processQueue(null, access);

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return clientApi(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem("access");
          localStorage.removeItem("refresh");
          processQueue(refreshError, null);
          
          // Redirect to login
          if (typeof window !== 'undefined') {
            window.location.href = "/login";
          }
          
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    }
  );
}

// For backward compatibility, export a default api
export const api = clientApi;

// Token helpers
export const isClient = typeof window !== 'undefined';

export const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem("access");
};

export const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem("refresh");
};

export const setTokens = (access: string, refresh: string) => {
  if (typeof window === 'undefined') return;
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
};

export const clearTokens = () => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

export const decodeToken = (token: string): any => {
  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
};

export const isTokenValid = (token: string): boolean => {
  const decoded = decodeToken(token);
  if (!decoded) return false;
  
  const currentTime = Date.now() / 1000;
  return decoded.exp > currentTime;
};

export const isTokenExpired = (token: string): boolean => {
  return !isTokenValid(token);
};

export const getTokenExpiry = (token: string): Date | null => {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return null;
  
  return new Date(decoded.exp * 1000);
};

export const getTokenRemainingTime = (token: string): number => {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return 0;
  
  return decoded.exp * 1000 - Date.now();
};