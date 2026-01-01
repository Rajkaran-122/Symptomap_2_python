import { useEffect, useState } from 'react';
import { useWebSocket } from './useWebSocket';
import { SymptoMapAPI } from '../services/api';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '') + '/api/v1/ws';

interface DashboardStats {
    active_outbreaks: number;
    hospitals_monitored: string;
    ai_predictions: number;
    coverage_area: string;
}

interface PerformanceMetrics {
    api_latency: string;
    api_latency_trend: number;
    active_users: string;
    active_users_trend: number;
    system_uptime: string;
    uptime_trend: number;
    last_sync: string;
}

interface RiskZones {
    high_risk_zones: number;
    at_risk_population: string;
}

/**
 * Custom hook for real-time dashboard statistics
 * 
 * Automatically refreshes stats when WebSocket events are received
 */
export const useRealTimeStats = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [performance, setPerformance] = useState<PerformanceMetrics | null>(null);
    const [riskZones, setRiskZones] = useState<RiskZones | null>(null);
    const [loading, setLoading] = useState(true);
    const { lastMessage, isConnected, connectionStatus } = useWebSocket(WS_URL);

    const fetchAllStats = async () => {
        try {
            // Fetch all stats in parallel
            const [dashboardData, perfData, riskData] = await Promise.all([
                SymptoMapAPI.getDashboardStats(),
                SymptoMapAPI.getPerformanceMetrics(),
                SymptoMapAPI.getRiskZones()
            ]);

            setStats(dashboardData);
            setPerformance(perfData);
            setRiskZones(riskData);
        } catch (error) {
            console.error('Error fetching stats:', error);
        } finally {
            setLoading(false);
        }
    };

    // Initial fetch
    useEffect(() => {
        fetchAllStats();
    }, []);

    // Refresh on WebSocket events
    useEffect(() => {
        if (lastMessage?.type === 'NEW_OUTBREAK' || lastMessage?.type === 'NEW_ALERT') {
            console.log('🔄 Refreshing stats due to real-time update');
            fetchAllStats();
        }
    }, [lastMessage]);

    return {
        stats,
        performance,
        riskZones,
        loading,
        isConnected,
        connectionStatus,
        refresh: fetchAllStats
    };
};
