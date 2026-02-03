
import requests

API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

def register_new_doctor():
    print(f"Creating Demo Doctor Account on {API_URL}")
    
    payload = {
        "email": "doctor_demo@symptomap.com",
        "password": "Doctor@SymptoMap2025", 
        "full_name": "Dr. Demo User",
        "role": "doctor",
        "phone": "+919876543299"
    }
    
    try:
        resp = requests.post(f"{API_URL}/auth/register", json=payload)
        
        if resp.status_code in [200, 201]:
            print("✅ SUCCESS! Account created.")
            print(f"   Email:    {payload['email']}")
            print(f"   Password: {payload['password']}")
        else:
            print(f"❌ Failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    register_new_doctor()
