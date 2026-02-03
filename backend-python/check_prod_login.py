import requests
import json

BASE_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

USERS = [
    {"email": "doctor@symptomap.com", "password": "Doctor@SymptoMap2025"},
    {"email": "doctor@symptomap.com", "password": "DoctorUser123!@#"},
    {"email": "admin@symptomap.com", "password": "admin123"},
]

print(f"Checking login on {BASE_URL}...")

for user in USERS:
    print(f"\nTrying {user['email']} / {user['password']} ...")
    try:
        # Try both JSON and Form Data just in case, though we know it should be Form
        
        # 1. Form Data (Standard OAuth2)
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": user['email'], "password": user['password']},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"✅ SUCCESS! (Form Data)")
            print(f"   Token: {resp.json().get('access_token')[:20]}...")
            continue
        else:
            print(f"   ❌ Failed (Form Data): {resp.status_code} - {resp.text}")

        # 2. JSON (Some custom auth implementations)
        resp = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": user['email'], "password": user['password']},
            timeout=10
        )
        if resp.status_code == 200:
            print(f"✅ SUCCESS! (JSON)")
            continue
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
