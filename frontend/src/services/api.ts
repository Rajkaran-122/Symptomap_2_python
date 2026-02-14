import axios from 'axios';

const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create instance with interceptor
const apiInstance = axios.create({
  baseURL: API_URL
});

apiInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('symptomap_access_token') || localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const SymptoMapAPI = {
  // Outbreak endpoints - uses /outbreaks/all to get approved doctor submissions
  getOutbreaks: async (params?: any) => {
    const response = await apiInstance.get('/outbreaks/all', { params });
    // Return outbreaks array from the response
    return response.data?.outbreaks || response.data || [];
  },

  getOutbreakStats: async () => {
    const response = await apiInstance.get('/outbreaks/stats');
    return response.data;
  },

  // Prediction endpoints
  getPredictions: async () => {
    const response = await apiInstance.get('/predictions/');
    return response.data;
  },

  // Statistics endpoints
  getDashboardStats: async () => {
    const response = await apiInstance.get('/stats/dashboard');
    return response.data;
  },

  getPerformanceMetrics: async () => {
    const response = await apiInstance.get('/stats/performance');
    return response.data;
  },

  getRiskZones: async () => {
    const response = await apiInstance.get('/stats/zones');
    return response.data;
  },

  getAnalyticsData: async () => {
    const response = await apiInstance.get('/stats/analytics');
    return response.data;
  },
};
