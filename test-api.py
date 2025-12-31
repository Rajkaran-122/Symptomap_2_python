"""
Test script to verify backend API endpoints
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

print("=" * 60)
print("SymptoMap Backend API Testing")
print("=" * 60)
print()

# Test 1: Health Check
print("Test 1: Health Check")
print("-" * 40)
try:
    response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health")
    print(f"✅ Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 2: Start Chatbot Conversation
print("Test 2: Start Chatbot Conversation")
print("-" * 40)
try:
    response = requests.post(
        f"{API_BASE}/chatbot/start",
        json={
            "user_info": {"age": 28, "gender": "male"},
            "location": {"city": "Mumbai", "country": "India"}
        }
    )
    print(f"✅ Status: {response.status_code}")
    data = response.json()
    session_id = data.get("session_id")
    print(f"   Session ID: {session_id}")
    print(f"   Message: {data.get('message')[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")
    session_id = None
print()

# Test 3: Send Message to Chatbot
if session_id:
    print("Test 3: Send Message to Chatbot")
    print("-" * 40)
    try:
        response = requests.post(
            f"{API_BASE}/chatbot/message",
            json={
                "session_id": session_id,
                "message": "I have fever and body ache for 2 days"
            }
        )
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Bot Response: {data['bot_messages'][0]['content'][:100]}...")
        print(f"   State: {data.get('conversation_state')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

# Test 4: Emergency Detection
print("Test 4: Emergency Detection")
print("-" * 40)
try:
    response = requests.post(
        f"{API_BASE}/chatbot/start",
        json={"user_info": None, "location": None}
    )
    emergency_session = response.json()["session_id"]
    
    response = requests.post(
        f"{API_BASE}/chatbot/message",
        json={
            "session_id": emergency_session,
            "message": "I have severe chest pain and difficulty breathing"
        }
    )
    data = response.json()
    print(f"✅ Status: {response.status_code}")
    print(f"   Emergency Detected: {data['bot_messages'][0].get('type') == 'emergency'}")
    print(f"   Response: {data['bot_messages'][0]['content'][:80]}...")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 5: List Outbreaks
print("Test 5: List Outbreaks")
print("-" * 40)
try:
    response = requests.get(f"{API_BASE}/outbreaks/")
    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"   Outbreaks found: {len(data)}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 6: List Predictions
print("Test 6: List Predictions")
print("-" * 40)
try:
    response = requests.get(f"{API_BASE}/predictions/")
    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"   Predictions found: {len(data)}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 7: List Alerts
print("Test 7: List Alerts")
print("-" * 40)
try:
    response = requests.get(f"{API_BASE}/alerts/")
    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"   Alerts found: {len(data)}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

print("=" * 60)
print("Testing Complete!")
print("=" * 60)
