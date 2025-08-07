/**
 * Mobile App Configuration
 * Switch between development and production environments
 */

// Use production backend for builds, with fallback to demo mode
const ENV = 'production';

const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
    API_TIMEOUT: 10000,
    DEBUG: true,
    DEMO_MODE: false,
  },
  production: {
    API_BASE_URL: 'https://restyleproject-production.up.railway.app',
    API_TIMEOUT: 15000,
    DEBUG: false,
    DEMO_MODE: false, // Set to true if backend is not available
  }
};

const currentConfig = config[ENV] || config.production;

console.log(`🚀 Mobile App Environment: ${ENV}`);
console.log(`📡 API Base URL: ${currentConfig.API_BASE_URL}`);
console.log(`🎭 Demo Mode: ${currentConfig.DEMO_MODE}`);

export default currentConfig; 