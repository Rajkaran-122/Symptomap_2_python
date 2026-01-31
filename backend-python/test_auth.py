import requests
import time
import sys

# Base URLs
API_URL = "http://localhost:8000/api/v1"
ROOT_URL = "http://localhost:8000"

EMAIL = f"test_user_{int(time.time())}@example.com"
PASSWORD = "TestUser123!@#"

def print_result(name, success, message=""):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {name}: {message}")
    if not success:
        # Don't exit immediately, try other tests if possible, unless critical
        if name != "Health Check":
             sys.exit(1)

def test_health():
    try:
        r = requests.get(f"{ROOT_URL}/health")
        print_result("Health Check", r.status_code == 200, r.text)
    except Exception as e:
        print_result("Health Check", False, str(e))

def test_register():
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
        "full_name": "Test User",
        "role": "doctor"
    }
    try:
        r = requests.post(f"{API_URL}/auth/register", json=payload)
        success = r.status_code == 200 or r.status_code == 201
        print_result("Registration", success, r.json() if success else r.text)
    except Exception as e:
        print_result("Registration", False, str(e))

def test_login():
    payload = {
        "username": EMAIL,
        "password": PASSWORD
    }
    try:
        r = requests.post(f"{API_URL}/auth/login", data=payload)
        if r.status_code == 200:
            data = r.json()
            print_result("Login", True, "Token received")
            return data["access_token"]
        else:
            print_result("Login", False, r.text)
            return None
    except Exception as e:
        print_result("Login", False, str(e))
        return None

def test_me(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{API_URL}/auth/me", headers=headers)
        print_result("Get Profile", r.status_code == 200, r.json().get("email"))
    except Exception as e:
        print_result("Get Profile", False, str(e))

def run_tests():
    print("🚀 Starting Auth Tests...")
    test_health()
    test_register()
    token = test_login()
    if token:
        test_me(token)
    else:
        print("⏭️ Skipping Profile test (no token)")
    print("✨ Tests complete!")

if __name__ == "__main__":
    run_tests()
