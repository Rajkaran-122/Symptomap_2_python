"""
Test script for Advanced Features (Image, PDF, Flagging)
"""

import requests
import json
import os
from PIL import Image
import io

API_BASE = "http://localhost:8000/api/v1"

def create_dummy_image():
    """Create a temporary dummy image for testing"""
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

print("=" * 60)
print("SymptoMap Advanced Feature Testing")
print("=" * 60)
print()

# 0. Health Check
print("Test 0: Checking Backend connection")
try:
    response = requests.get(f"http://localhost:8000/health")
    if response.status_code != 200:
        print("❌ Backend is not healthy or running.")
        exit(1)
    print("✅ Backend is running.")
except:
    print("❌ Could not connect to backend. Please start it with 'uvicorn app.main:app --reload'")
    exit(1)
print()

# 1. Start a Session
print("Test 1: Creating Chat Session")
session_id = None
try:
    response = requests.post(
        f"{API_BASE}/chatbot/start",
        json={"user_info": {"age": 30}, "location": {"city": "Test City"}}
    )
    if response.status_code == 200:
        session_id = response.json().get("session_id")
        print(f"✅ Session Created: {session_id}")
    else:
        print(f"❌ Failed to create session: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
print()

# 2. Test Image Upload
print("Test 2: Image Upload")
print("-" * 40)
try:
    img_data = create_dummy_image()
    files = {'file': ('test_rash.jpg', img_data, 'image/jpeg')}
    params = {'session_id': session_id}
    
    response = requests.post(
        f"{API_BASE}/chatbot/upload-image",
        params=params, 
        files=files
    )
    
    if response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        print(f"   Analysis: {response.json().get('message')}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# 3. Test Flagging
print("Test 3: Flag Conversation")
print("-" * 40)
try:
    payload = {"reason": "Test flagging for review"}
    response = requests.post(
        f"{API_BASE}/chatbot/flag/{session_id}",
        json=payload
    )
    
    if response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# 4. Test PDF Export
print("Test 4: PDF Export")
print("-" * 40)
try:
    response = requests.get(f"{API_BASE}/chatbot/export-pdf/{session_id}")
    
    if response.status_code == 200:
        content_type = response.headers.get('content-type')
        print(f"✅ Status: {response.status_code}")
        print(f"   Content-Type: {content_type}")
        print(f"   Size: {len(response.content)} bytes")
        
        if 'application/pdf' in content_type:
            with open("test_report.pdf", "wb") as f:
                f.write(response.content)
            print("   ✅ Saved to test_report.pdf")
        else:
            print("   ❌ Did not receive PDF content type")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

print("=" * 60)
print("Advanced Testing Complete!")
print("=" * 60)
