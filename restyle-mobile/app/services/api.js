import axios from 'axios';
import config from '../../config.js';

const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  // ... any other config ...
});

console.log('API baseURL:', api.defaults.baseURL);

export default api; 