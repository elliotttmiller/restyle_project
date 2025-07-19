/**
 * Mobile App Configuration
 * Switch between development and production environments
 */

// Force production for now to ensure Railway connection
const ENV = 'production';

const config = {
  development: {
    API_BASE_URL: 'http://192.168.0.33:8000',
    API_TIMEOUT: 10000,
    DEBUG: true,
  },
  production: {
    API_BASE_URL: 'https://restyleproject-production.up.railway.app',
    API_TIMEOUT: 15000,
    DEBUG: false,
  }
};

const currentConfig = config[ENV] || config.production;

console.log(`🚀 Mobile App Environment: ${ENV}`);
console.log(`📡 API Base URL: ${currentConfig.API_BASE_URL}`);

export default currentConfig; 