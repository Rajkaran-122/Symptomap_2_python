import requests
import json
print("Running script v3 - No Phone Field")

url = "http://localhost:8000/api/v1/auth/register"
headers = {"Content-Type": "application/json"}
data = {
    "email": "test.patient.final@example.com",
    "password": "Password@123",
    "full_name": "Final Test Patient",
    "role": "patient"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
