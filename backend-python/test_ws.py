import asyncio
import websockets
import json

async def test_websocket():
    # uri = "ws://localhost:8000/api/v1/ws"
    uri = "wss://symptomap-2-python-1.onrender.com/api/v1/ws"
    
    print(f"Attempting connection to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for welcome message
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
            # Send ping
            print("📤 Sending 'ping'...")
            await websocket.send("ping")
            
            # Wait for pong
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
