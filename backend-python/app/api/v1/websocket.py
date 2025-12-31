"""
WebSocket API endpoints for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.websocket.manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data synchronization
    
    Clients connect to this endpoint to receive real-time updates about:
    - New outbreaks
    - New alerts
    - Statistics changes
    - System notifications
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive by receiving messages
            # Clients can send ping messages to keep connection active
            data = await websocket.receive_text()
            
            # Handle client messages (optional)
            if data == "ping":
                await websocket.send_text("pong")
            
            logger.debug(f"Received from client: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/status")
async def websocket_status():
    """
    Get WebSocket server status
    
    Returns:
        Current number of active connections
    """
    return {
        "status": "running",
        "active_connections": manager.get_connection_count(),
        "server": "SymptoMap WebSocket Server v1.0"
    }
