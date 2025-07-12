import axios from 'axios';
import { useAuthStore } from './authStore';

const API_BASE_URL = "http://192.168.0.25:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Sending token with request:', token);
    } else {
      console.log('No token found in store!');
    }
    return config;
  },
  (error) => Promise.reject(error)
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
          // No refresh token available, logout
          console.log('No refresh token available, logging out');
          useAuthStore.getState().logout();
          return Promise.reject(error);
        }
        
        console.log('Attempting to refresh token...');
        
        // Attempt to refresh the token
        const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        
        // Update the store with the new access token
        useAuthStore.getState().setTokens(access, refreshToken);
        
        console.log('Token refreshed successfully');
        
        // Retry the original request with the new token
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed, logout
        console.error('Token refresh failed:', refreshError);
        useAuthStore.getState().logout();
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api; 