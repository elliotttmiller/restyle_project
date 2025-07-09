import axios from 'axios';
import { useAuthStore } from './authStore';

const API_BASE_URL = "http://192.168.0.13:8000/api";

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

export default api; 