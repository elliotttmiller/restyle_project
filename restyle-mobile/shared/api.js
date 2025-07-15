import axios from 'axios';
import { useAuthStore } from './authStore';

const API_BASE_URL = "http://192.168.0.33:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor: Adds the auth token to every outgoing request.
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handles expired tokens and automatically refreshes them.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const { refreshToken, setTokens, logout } = useAuthStore.getState();
      if (!refreshToken) {
        console.log('No refresh token available, logging out.');
        logout();
        return Promise.reject(error);
      }
      try {
        console.log('Access token expired. Attempting to refresh...');
        const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
          refresh: refreshToken,
        });
        const { access: newAccessToken } = response.data;
        setTokens(newAccessToken, refreshToken);
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed. Logging out.', refreshError);
        logout();
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default api; 