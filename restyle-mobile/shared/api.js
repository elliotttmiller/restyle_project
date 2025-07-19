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

// Add request logging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers
    });
    
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response logging
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });
    return Promise.reject(error);
  }
);

// --- UPGRADED TOKEN REFRESH LOGIC ---
let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
}

// Helper to decode JWT and get expiry
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

// Proactive refresh timer
let refreshTimeout = null;
function scheduleProactiveRefresh(token, refreshToken, setTokens, logout) {
  if (refreshTimeout) clearTimeout(refreshTimeout);
  const payload = parseJwt(token);
  if (payload && payload.exp) {
    const expiresIn = payload.exp * 1000 - Date.now();
    // Refresh 1 minute before expiry
    const refreshIn = Math.max(expiresIn - 60 * 1000, 0);
    if (refreshIn > 0) {
      refreshTimeout = setTimeout(async () => {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, { refresh: refreshToken });
          const { access: newAccessToken } = response.data;
          setTokens(newAccessToken, refreshToken);
          scheduleProactiveRefresh(newAccessToken, refreshToken, setTokens, logout);
        } catch (e) {
          logout();
        }
      }, refreshIn);
    }
  }
}

// Patch setTokens to always schedule proactive refresh
const origSetTokens = useAuthStore.getState().setTokens;
useAuthStore.setState({
  setTokens: (accessToken, refreshToken) => {
    origSetTokens(accessToken, refreshToken);
    const { setTokens, logout } = useAuthStore.getState();
    if (accessToken && refreshToken) {
      scheduleProactiveRefresh(accessToken, refreshToken, setTokens, logout);
    } else if (refreshTimeout) {
      clearTimeout(refreshTimeout);
    }
  }
});

// On app load, schedule proactive refresh if tokens exist
const { token, refreshToken, setTokens, logout } = useAuthStore.getState();
if (token && refreshToken) {
  scheduleProactiveRefresh(token, refreshToken, setTokens, logout);
}

// --- END UPGRADED LOGIC ---

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue the request until refresh is done
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
        .then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        })
        .catch(err => Promise.reject(err));
      }
      originalRequest._retry = true;
      isRefreshing = true;
      const { refreshToken, setTokens, logout } = useAuthStore.getState();
      if (!refreshToken) {
        logout();
        isRefreshing = false;
        processQueue(new Error('No refresh token'));
        return Promise.reject(error);
      }
      try {
        const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, { refresh: refreshToken });
        const { access: newAccessToken } = response.data;
        setTokens(newAccessToken, refreshToken);
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return api(originalRequest);
      } catch (refreshError) {
        logout();
        processQueue(refreshError, null);
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api; 