// File: frontend/src/services/api.js
import axios from 'axios';
import useAuthStore from '../store/authStore';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// This interceptor runs before every single request
api.interceptors.request.use(
  (config) => {
    // It gets the state directly from the store
    const token = useAuthStore.getState().accessToken; 
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for automated token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 (Unauthorized) and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) {
          // No refresh token available, redirect to login
          useAuthStore.getState().logout();
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // Attempt to refresh the token
        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        
        // Update the store with the new access token
        useAuthStore.getState().login({
          access,
          refresh: refreshToken // Keep the same refresh token
        });
        
        // Retry the original request with the new token
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed, logout and redirect to login
        console.error('Token refresh failed:', refreshError);
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;