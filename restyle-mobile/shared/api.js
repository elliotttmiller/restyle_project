import axios from 'axios';
import { useAuthStore } from './authStore';
import config from '../config.js';

export const API_BASE_URL = config.API_BASE_URL;

console.log('🔧 API Configuration:', {
  API_BASE_URL,
  config: config
});

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: config.API_TIMEOUT || 15000,
});

// Add request logging and authentication
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
    });
    
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Added auth token to request');
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response logging and simple error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  async (error) => {
    console.error('❌ API Response Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });

    // Handle 401 unauthorized errors
    if (error.response?.status === 401) {
      console.log('🔒 Unauthorized request detected');
      const { logout } = useAuthStore.getState();
      
      // For now, just logout on 401 errors
      // TODO: Implement token refresh later
      logout();
    }

    return Promise.reject(error);
  }
);

export default api; 