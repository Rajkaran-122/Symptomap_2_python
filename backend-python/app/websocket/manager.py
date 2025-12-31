"""
WebSocket Connection Manager
Manages WebSocket connections and broadcasts real-time events to all connected clients
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and event broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        logger.info("ConnectionManager initialized")
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
            
            # Send welcome message
            await websocket.send_json({
                "type": "CONNECTION_ESTABLISHED",
                "message": "Connected to SymptoMap real-time server",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            raise
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients
        
        Args:
            message: Dictionary containing event type and data
        """
        if not self.active_connections:
            logger.debug("No active connections to broadcast to")
            return
        
        # Add timestamp to message
        message["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"Broadcasting {message.get('type')} to {len(self.active_connections)} clients")
        
        # Send to all connections, remove failed ones
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Clean up failed connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
