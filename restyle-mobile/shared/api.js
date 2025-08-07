import axios from 'axios';
import { useAuthStore } from './authStore';
import config from '../config.js';
import { DemoDataService } from './demoData.js';

export const API_BASE_URL = config.API_BASE_URL;

console.log('🔧 API Configuration:', {
  API_BASE_URL,
  config: config
});

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: config.API_TIMEOUT || 15000,
});

// Track if backend is available
let backendAvailable = true;
let lastHealthCheck = 0;
const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds

// Check backend health periodically
const checkBackendHealth = async () => {
  const now = Date.now();
  if (now - lastHealthCheck < HEALTH_CHECK_INTERVAL) {
    return backendAvailable;
  }
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/core/health/`, { timeout: 5000 });
    backendAvailable = response.status === 200;
    console.log('✅ Backend health check passed');
  } catch (error) {
    backendAvailable = false;
    console.log('❌ Backend health check failed:', error.message);
  }
  
  lastHealthCheck = now;
  return backendAvailable;
};

// Add request logging and authentication
api.interceptors.request.use(
  async (config) => {
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

// Add response logging and smart error handling with fallbacks
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    backendAvailable = true;
    return response;
  },
  async (error) => {
    console.error('❌ API Response Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });

    // Mark backend as unavailable on network errors
    if (!error.response || error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
      backendAvailable = false;
    }

    // Handle 401 unauthorized errors
    if (error.response?.status === 401) {
      console.log('🔒 Unauthorized request detected');
      const { logout } = useAuthStore.getState();
      logout();
    }

    return Promise.reject(error);
  }
);

// Enhanced API wrapper with demo fallbacks
const apiWrapper = {
  async get(url, config = {}) {
    try {
      return await api.get(url, config);
    } catch (error) {
      // If backend is not available and it's a known endpoint, return demo data
      if (!await checkBackendHealth()) {
        return handleOfflineResponse(url, 'GET', error);
      }
      throw error;
    }
  },

  async post(url, data, config = {}) {
    try {
      return await api.post(url, data, config);
    } catch (error) {
      // If backend is not available and it's a known endpoint, return demo data
      if (!await checkBackendHealth()) {
        return handleOfflineResponse(url, 'POST', error, data);
      }
      throw error;
    }
  },

  // Pass through other methods
  put: api.put.bind(api),
  delete: api.delete.bind(api),
  patch: api.patch.bind(api),
  defaults: api.defaults
};

async function handleOfflineResponse(url, method, originalError, data = null) {
  console.log('🎭 Backend unavailable, using demo data for:', url);
  
  // Add realistic delay to simulate network request
  await DemoDataService.delay(800);
  
  if (url.includes('/core/ebay-search/')) {
    const query = url.includes('?') ? new URLSearchParams(url.split('?')[1]).get('q') : 'demo';
    return {
      data: {
        status: 'success',
        results: DemoDataService.getEbaySearchResults(query || 'demo'),
        demo_mode: true,
        message: 'Demo mode: Backend unavailable'
      },
      status: 200
    };
  }
  
  if (url.includes('/core/price-analysis/')) {
    const query = data?.title || 'demo item';
    return {
      data: {
        ...DemoDataService.getPriceAnalysis(query),
        demo_mode: true,
        message: 'Demo mode: Backend unavailable'
      },
      status: 200
    };
  }
  
  if (url.includes('/core/health/')) {
    return {
      data: {
        ...DemoDataService.getSystemStatus(),
        demo_mode: true,
        message: 'Demo mode: Backend unavailable'
      },
      status: 200
    };
  }
  
  if (url.includes('/core/metrics/')) {
    return {
      data: {
        ...DemoDataService.getPerformanceMetrics(),
        demo_mode: true,
        message: 'Demo mode: Backend unavailable'
      },
      status: 200
    };
  }
  
  if (url.includes('/core/ai/advanced-search/')) {
    return {
      data: {
        ...DemoDataService.getImageAnalysis(),
        demo_mode: true,
        message: 'Demo mode: Backend unavailable'
      },
      status: 200
    };
  }
  
  // For unknown endpoints, throw the original error
  throw originalError;
}

export default apiWrapper; 