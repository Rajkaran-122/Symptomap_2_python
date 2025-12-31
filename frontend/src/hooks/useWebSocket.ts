import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
    type: string;
    data?: any;
    message?: string;
    timestamp?: string;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    lastMessage: WebSocketMessage | null;
    sendMessage: (message: string) => void;
    connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
}

/**
 * Custom React hook for WebSocket real-time connections
 * 
 * Auto-reconnects on disconnect and provides connection status
 * 
 * @param url - WebSocket URL (e.g., 'ws://localhost:8000/api/v1/ws')
 * @returns WebSocket connection state and utilities
 */
export const useWebSocket = (url: string): UseWebSocketReturn => {
    const ws = useRef<WebSocket | null>(null);
    const reconnectTimeout = useRef<NodeJS.Timeout>();
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');

    const connect = useCallback(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setConnectionStatus('connecting');
        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            console.log('✅ WebSocket Connected');
            setIsConnected(true);
            setConnectionStatus('connected');

            // Clear any existing reconnect timeout
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
        };

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 WebSocket Message:', data);
                setLastMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.current.onclose = () => {
            console.log('❌ WebSocket Disconnected');
            setIsConnected(false);
            setConnectionStatus('disconnected');

            // Auto-reconnect after 3 seconds
            reconnectTimeout.current = setTimeout(() => {
                console.log('🔄 Attempting to reconnect...');
                connect();
            }, 3000);
        };

        ws.current.onerror = (error) => {
            console.error('⚠️ WebSocket Error:', error);
            setConnectionStatus('error');
        };
    }, [url]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((message: string) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(message);
        } else {
            console.warn('WebSocket is not connected');
        }
    }, []);

    return { isConnected, lastMessage, sendMessage, connectionStatus };
};
