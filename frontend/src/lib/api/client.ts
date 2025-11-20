import axios from 'axios';

// Get API URL from environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Log API URL in development mode
if (import.meta.env.DEV) {
  console.log('🔗 API Base URL:', API_BASE_URL);
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for production
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here if needed in the future
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error: No response from server');
    } else {
      // Something else happened
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
