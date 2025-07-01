// frontend/src/services/api.js
import axios from 'axios';
import useAuthStore from '../store/authStore';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Our Django API base URL
});

// This is an interceptor. It runs before every request is sent.
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      // If a token exists, add it to the Authorization header.
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;