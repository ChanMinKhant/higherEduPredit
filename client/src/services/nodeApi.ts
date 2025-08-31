import axios from 'axios';

axios.defaults.withCredentials = true;

export const backendUrl = 'http://localhost:3000/api';

const apiService = axios.create({
  baseURL: backendUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export default apiService;
