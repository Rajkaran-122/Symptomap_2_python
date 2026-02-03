
import requests
import sys
import json

# Production API URL
API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

def register_doctor():
    print(f"🏥 Creating Doctor Account on Production: {API_URL}")
    print("-" * 50)
    
    endpoint = f"{API_URL}/auth/register"
    
    payload = {
        "email": "doctor@symptomap.com",
        "password": "Doctor@SymptoMap2025",  # Must meet complexity requirements
        "full_name": "Dr. Sarah Smith",
        "role": "doctor",  # If allowed by public registration
        "phone": "+919876543210"
    }
    
    try:
        print(f"Sending registration request for {payload['email']}...")
        resp = requests.post(endpoint, json=payload)
        
        if resp.status_code == 201 or resp.status_code == 200:
            print("✅ SUCCESS! Doctor account created.")
            print(f"   Email:    {payload['email']}")
            print(f"   Password: {payload['password']}")
            print("\n👉 You can now log in at the Doctor Station.")
        elif resp.status_code == 400:
            if "already exists" in resp.text:
                print("⚠️  User already exists. (But login failed??)")
            else:
                print(f"❌ Registration Failed (400): {resp.text}")
        elif resp.status_code == 422:
             print(f"❌ Validation Error (422): {resp.text}")
             print("Double check password complexity or email format.")
        else:
            print(f"❌ Error {resp.status_code}: {resp.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    register_doctor()
