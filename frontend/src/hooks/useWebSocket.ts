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
    const reconnectDelay = useRef(5000);  // Start with 5s for cold starts
    const MAX_RECONNECT_DELAY = 60000;  // 60 seconds max (Render cold starts can take time)
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');

    const connect = useCallback(() => {
        if (ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
            return;
        }

        setConnectionStatus('connecting');

        try {
            ws.current = new WebSocket(url);
        } catch (err) {
            // Silently fail and schedule reconnect
            console.warn('WebSocket connection failed, will retry...');
            setConnectionStatus('disconnected');
            reconnectTimeout.current = setTimeout(() => {
                connect();
            }, reconnectDelay.current);
            return;
        }

        ws.current.onopen = () => {
            console.log('✅ WebSocket Connected');
            setIsConnected(true);
            setConnectionStatus('connected');
            reconnectDelay.current = 3000;  // Reset delay on successful connection

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

            // Auto-reconnect with exponential backoff
            reconnectTimeout.current = setTimeout(() => {
                console.log(`🔄 Attempting to reconnect (delay: ${reconnectDelay.current}ms)...`);
                connect();
                // Increase delay for next time, up to max
                reconnectDelay.current = Math.min(reconnectDelay.current * 1.5, MAX_RECONNECT_DELAY);
            }, reconnectDelay.current);
        };

        ws.current.onerror = (error) => {
            console.warn('⚠️ WebSocket Error (will reconnect):', error);
            setConnectionStatus('error');
        };
    }, [url]);

    useEffect(() => {
        // Only connect if the page is visible
        if (document.visibilityState === 'visible') {
            connect();
        }

        // Handle visibility change - reconnect when user returns to tab
        const handleVisibilityChange = () => {
            if (document.visibilityState === 'visible') {
                // Tab became visible, check connection
                if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
                    console.log('🔄 Tab visible, reconnecting WebSocket...');
                    reconnectDelay.current = 1000; // Quick reconnect when returning
                    connect();
                }
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);

            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (ws.current) {
                // Remove listeners to prevent "onclose" from triggering reconnect
                // when we intentionally close the connection (e.g. Strict Mode or unmount)
                ws.current.onclose = null;
                ws.current.onerror = null;
                ws.current.onmessage = null;
                ws.current.onopen = null;
                if (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING) {
                    ws.current.close();
                }
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
