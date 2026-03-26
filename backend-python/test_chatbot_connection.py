import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_chatbot():
    print("1. Starting Chatbot Conversation...")
    try:
        start_res = requests.post(f"{BASE_URL}/chatbot/start", json={})
        if start_res.status_code != 200:
            print(f"FAILED to start conversation: {start_res.text}")
            return
        
        data = start_res.json()
        session_id = data.get("session_id")
        print(f"SUCCESS: Session ID: {session_id}")
        print(f"Greeting: {data.get('message')[:50]}...")

        # Test Message
        print("\n2. Sending Test Message ('I have a headache')...")
        msg_payload = {
            "session_id": session_id,
            "message": "I have a headache"
        }
        
        msg_res = requests.post(f"{BASE_URL}/chatbot/message", json=msg_payload)
        
        if msg_res.status_code == 200:
            response = msg_res.json()
            bot_msg = response.get("bot_messages", [{}])[0].get("content", "")
            print(f"SUCCESS: Bot replied: {bot_msg[:100]}...")
        else:
            print(f"FAILED to send message: {msg_res.text}")
            print("Check if OPENAI_API_KEY is set correctly in backend-python/.env")

    except Exception as e:
        print(f"ERROR: Could not connect to backend. Is it running? {e}")

if __name__ == "__main__":
    test_chatbot()
