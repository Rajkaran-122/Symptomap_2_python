import requests
import time
import sys

# Base URLs
API_URL = "http://localhost:8000/api/v1"

# Credentials
DOCTOR_EMAIL = "doctor@symptomap.com"
DOCTOR_PASSWORD = "DoctorUser123!@#"

def print_result(name, success, message=""):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {name}: {message}")
    if not success:
        # Continue even if failed, to see full picture
        pass

def get_token():
    payload = {
        "username": DOCTOR_EMAIL,
        "password": DOCTOR_PASSWORD
    }
    try:
        r = requests.post(f"{API_URL}/auth/login", data=payload)
        if r.status_code == 200:
            return r.json()["access_token"]
        else:
            print(f"❌ Auth Failed: {r.text}")
            return None
    except Exception as e:
        print(f"❌ Auth Exception: {e}")
        return None

def test_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test Stats
    try:
        r = requests.get(f"{API_URL}/doctor/stats", headers=headers)
        print_result("Stats Endpoint", r.status_code == 200, f"Status: {r.status_code}")
    except Exception as e:
        print_result("Stats Endpoint", False, str(e))

    # 2. Test Outbreaks List
    try:
        r = requests.get(f"{API_URL}/outbreaks", params={"limit": 5})
        print_result("Public Outbreaks", r.status_code == 200, f"Count: {len(r.json()) if r.status_code==200 else 'Err'}")
    except Exception as e:
        print_result("Public Outbreaks", False, str(e))
        
    # 3. Test Doctor Submissions
    try:
        r = requests.get(f"{API_URL}/doctor/submissions", headers=headers)
        print_result("Doctor Submissions", r.status_code == 200, f"Status: {r.status_code}")
    except Exception as e:
        print_result("Doctor Submissions", False, str(e))

if __name__ == "__main__":
    print("🚀 Testing API Endpoints...")
    token = get_token()
    if token:
        test_endpoints(token)
    else:
        print("Cannot proceed without token")
