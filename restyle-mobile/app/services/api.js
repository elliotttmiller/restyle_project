import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.0.33:8000',
  // ... any other config ...
});

console.log('API baseURL:', api.defaults.baseURL);

export default api; 