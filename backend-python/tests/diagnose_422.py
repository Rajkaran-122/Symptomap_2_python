import requests
import time
import random

BASE_URL = "http://localhost:8000/api/v1/auth/otp"

def diagnose():
    print("--- Diagnosing Signup 422 Error ---")
    rnd = int(time.time())
    email = f"user_{rnd}@symptomap.com"
    
    # Test cases
    payloads = [
        {
            "name": "Raw 10 digit phone",
            "data": {
                "email": email,
                "phone": "9876543210", 
                "password": "Password@123", 
                "full_name": "Test User",
                "role": "user"
            }
        },
        {
            "name": "Formatted +91 phone",
            "data": {
                "email": f"user2_{rnd}@symptomap.com",
                "phone": "+919876543210", 
                "password": "Password@123", 
                "full_name": "Test User",
                "role": "user"
            }
        }
    ]

    for p in payloads:
        print(f"\nTesting: {p['name']}")
        try:
            response = requests.post(f"{BASE_URL}/signup", json=p['data'])
            print(f"Status: {response.status_code}")
            if response.status_code == 422:
                print("❌ Validation Error Details:")
                print(response.json())
            elif response.status_code == 201:
                print("✅ Success")
            else:
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    diagnose()
