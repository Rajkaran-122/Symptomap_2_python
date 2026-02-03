
import requests
import json
from datetime import datetime

URL = "https://symptomap-2-python-1.onrender.com/api/v1"
EMAIL = "admin@symptomap.com"
PASSWORD = "admin123"

def test_submission():
    print(f"🔬 Testing Doctor Submission at {URL}...")
    
    sess = requests.Session()
    
    # 1. Login
    print("1. Logging in...")
    try:
        resp = sess.post(f"{URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"❌ Login failed: {resp.status_code}")
            print(resp.text)
            return
        
        token = resp.json()["access_token"]
        sess.headers["Authorization"] = f"Bearer {token}"
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Submit Outbreak
    print("2. Submitting test outbreak...")
    payload = {
        "disease_type": "Dengue",
        "patient_count": 5,
        "severity": "mild",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "location_name": "Test Hospital",
        "city": "Delhi",
        "state": "Delhi",
        "description": "Test submission for verification",
        "date_reported": datetime.now().isoformat()
    }
    
    try:
        resp = sess.post(f"{URL}/doctor/outbreak", json=payload)
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
        if resp.status_code in [200, 201]:
            print("✅ Submission successful!")
        else:
            print("❌ Submission failed!")
            
    except Exception as e:
        print(f"❌ Submission error: {e}")

if __name__ == "__main__":
    test_submission()
