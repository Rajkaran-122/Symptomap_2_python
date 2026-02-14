
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

export interface PublicStats {
    activeOutbreaks: number;
    activeBroadcasts: number;
    casesThisWeek: number;
    trendPercentage: number;
    regionsAffected: number;
    verifiedSources: number;
}

export interface Hotspot {
    city: string;
    risk: 'Critical' | 'High' | 'Moderate' | 'Low';
    color: string;
    count: number;
}

export interface Broadcast {
    id: string;
    title: string;
    message: string;
    severity: 'info' | 'warning' | 'critical';
    category: string;
    created_at: string;
    source: string;
}

class PublicService {
    /**
     * Fetch public dashboard statistics
     */
    async getStats(): Promise<PublicStats> {
        try {
            const response = await axios.get(`${API_BASE_URL}/public/stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch public stats:', error);
            // Return fallback data to prevent UI crash
            return {
                activeOutbreaks: 0,
                activeBroadcasts: 0,
                casesThisWeek: 0,
                trendPercentage: 0,
                regionsAffected: 0,
                verifiedSources: 0
            };
        }
    }

    /**
     * Fetch top hotspots
     */
    async getHotspots(): Promise<Hotspot[]> {
        try {
            const response = await axios.get(`${API_BASE_URL}/public/hotspots`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch hotspots:', error);
            return [];
        }
    }

    /**
     * Fetch active public broadcasts
     */
    async getBroadcasts(): Promise<Broadcast[]> {
        try {
            const response = await axios.get(`${API_BASE_URL}/public/broadcasts?limit=5`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch broadcasts:', error);
            return [];
        }
    }
    /**
     * Fetch live surveillance grid stats
     */
    async getGridStats(): Promise<any> {
        try {
            const response = await axios.get(`${API_BASE_URL}/public/grid-stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch grid stats:', error);
            return {
                visual_clusters: 0,
                active_zones: 0,
                risk_severe: 0,
                risk_moderate: 0
            };
        }
    }
}

export const publicService = new PublicService();
