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

export default api;