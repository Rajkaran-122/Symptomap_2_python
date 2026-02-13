"""Diagnose the exact error from OTP endpoints"""
import urllib.request, json, traceback

url = "http://localhost:8000/api/v1/auth/otp/signup"
data = json.dumps({
    "email": "diag@demo.com",
    "phone": "+911234567890",
    "password": "MyStr0ng@Pass!",
    "full_name": "Diag User",
    "role": "user"
}).encode("utf-8")

try:
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    r = urllib.request.urlopen(req)
    print(f"Status: {r.status}")
    print(f"Body: {r.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"HTTP {e.code}")
    print(f"Body: {body}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
