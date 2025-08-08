import axios from 'axios';
import config from '../../config.js';
import logger from '../../shared/logger';

const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  // ... any other config ...
});

logger.info('API baseURL:', api.defaults.baseURL);

export default api; 