
import asyncio
import websockets
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/api/v1/ws"

async def test_websocket():
    print(f"Testing WebSocket connection to {WS_URL}...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket Connected!")
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"📨 Received: {response}")
            if response == "pong":
                print("✅ WebSocket Heartbeat Successful!")
            return True
    except Exception as e:
        print(f"❌ WebSocket Connection Failed: {e}")
        return False

def test_cors():
    print("\nTesting CORS Preflight (OPTIONS) for /outbreaks/verify...")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type"
    }
    try:
        response = requests.options(f"{BASE_URL}/outbreaks/test-id/verify", headers=headers)
        print(f"Response Status: {response.status_code}")
        print("Response Headers:")
        for k, v in response.headers.items():
            if "access-control" in k.lower():
                print(f"  {k}: {v}")
        
        if "Access-Control-Allow-Origin" in response.headers:
            print("✅ CORS Headers Present!")
        else:
            print("❌ CORS Headers Missing!")
            
    except Exception as e:
        print(f"❌ CORS Request Failed: {e}")

if __name__ == "__main__":
    test_cors()
    asyncio.run(test_websocket())
