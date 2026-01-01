import axios from 'axios';

const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const SymptoMapAPI = {
  // Outbreak endpoints - uses /outbreaks/all to get approved doctor submissions
  getOutbreaks: async (params?: any) => {
    const response = await axios.get(`${API_URL}/outbreaks/all`, { params });
    // Return outbreaks array from the response
    return response.data?.outbreaks || response.data || [];
  },

  // Prediction endpoints
  getPredictions: async () => {
    const response = await axios.get(`${API_URL}/predictions/`);
    return response.data;
  },

  // Statistics endpoints
  getDashboardStats: async () => {
    const response = await axios.get(`${API_URL}/stats/dashboard`);
    return response.data;
  },

  getPerformanceMetrics: async () => {
    const response = await axios.get(`${API_URL}/stats/performance`);
    return response.data;
  },

  getRiskZones: async () => {
    const response = await axios.get(`${API_URL}/stats/zones`);
    return response.data;
  },

  getAnalyticsData: async () => {
    const response = await axios.get(`${API_URL}/stats/analytics`);
    return response.data;
  },
};
