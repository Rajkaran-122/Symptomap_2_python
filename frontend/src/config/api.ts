// Centralized API configuration
// This file provides the base API URL for all frontend components

const getApiUrl = (): string => {
    // Check for environment variable (set in Vercel)
    const envUrl = (import.meta as any).env?.VITE_API_URL;
    if (envUrl) {
        return envUrl;
    }

    // Fallback based on hostname
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;

        // Production on Vercel - use Render backend
        if (hostname.includes('vercel.app') || hostname.includes('symptomap')) {
            return 'https://symptomap-2-python-1.onrender.com/api/v1';
        }
    }

    // Local development fallback
    return 'http://localhost:8000/api/v1';
};

export const API_BASE_URL = getApiUrl();

// WebSocket URL
export const getWsUrl = (): string => {
    const apiUrl = API_BASE_URL;
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const baseUrl = apiUrl.replace(/^https?:\/\//, '').replace('/api/v1', '');
    return `${wsProtocol}://${baseUrl}/api/v1/ws`;
};

export const WS_URL = getWsUrl();

export default API_BASE_URL;
