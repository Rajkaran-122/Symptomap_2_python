import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';
import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '') + '/api/v1/ws';

interface DashboardStats {
    active_outbreaks: number;
    hospitals_monitored: string;
    ai_predictions: number;
    coverage_area: string;
}

/**
 * Custom hook for real-time dashboard statistics
 * 
 * Automatically refreshes stats when WebSocket events are received
 */
export const useRealTimeStats = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const { lastMessage, isConnected, connectionStatus } = useWebSocket(WS_URL);

    const fetchStats = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_BASE_URL}/stats/dashboard`);
            setStats(response.data);
        } catch (error) {
            console.error('Error fetching stats:', error);
        } finally {
            setLoading(false);
        }
    };

    // Initial fetch
    useEffect(() => {
        fetchStats();
    }, []);

    // Refresh on WebSocket events
    useEffect(() => {
        if (lastMessage?.type === 'NEW_OUTBREAK' || lastMessage?.type === 'NEW_ALERT') {
            console.log('🔄 Refreshing stats due to real-time update');
            fetchStats();
        }
    }, [lastMessage]);

    return { stats, loading, isConnected, connectionStatus, refresh: fetchStats };
};
