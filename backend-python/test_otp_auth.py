"""
OTP Auth Endpoint Verification Script
Run with: python test_otp_auth.py
Requires: Backend running on http://localhost:8000
"""

import urllib.request
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000/api/v1/auth/otp"
PASS = 0
FAIL = 0


def test(name, method, path, data=None, headers=None, expect_status=200):
    global PASS, FAIL
    url = BASE + path
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"  {method} {url}")

    try:
        body = json.dumps(data).encode("utf-8") if data else None
        h = {"Content-Type": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        r = urllib.request.urlopen(req)
        result = json.loads(r.read().decode("utf-8"))
        status = r.status

        if status == expect_status:
            print(f"  PASS - Status {status}")
            PASS += 1
        else:
            print(f"  FAIL - Expected {expect_status}, got {status}")
            FAIL += 1

        print(f"  Response: {json.dumps(result, indent=2)}")
        return result, status

    except urllib.error.HTTPError as e:
        result = json.loads(e.read().decode("utf-8"))
        status = e.code

        if status == expect_status:
            print(f"  PASS - Status {status} (expected)")
            PASS += 1
        else:
            print(f"  FAIL - Expected {expect_status}, got {status}")
            FAIL += 1

        print(f"  Response: {json.dumps(result, indent=2)}")
        return result, status

    except Exception as e:
        print(f"  FAIL - Exception: {e}")
        FAIL += 1
        return None, 0


def main():
    global PASS, FAIL

    print("=" * 60)
    print("OTP AUTH ENDPOINT VERIFICATION")
    print("=" * 60)

    # 1. Status endpoint
    test("GET /status - Health check", "GET", "/status")

    # 2. Signup
    test("POST /signup - New user", "POST", "/signup", {
        "email": "testuser@demo.com",
        "phone": "+919876543210",
        "password": "MyStr0ng@Pass!",
        "full_name": "Test User",
        "role": "user"
    }, expect_status=201)

    # 3. Login (expect OTP required or 403 if unverified)
    test("POST /login - User login (unverified)", "POST", "/login", {
        "email": "testuser@demo.com",
        "password": "MyStr0ng@Pass!"
    }, expect_status=403)

    # 4. Login wrong password
    test("POST /login - Wrong password", "POST", "/login", {
        "email": "testuser@demo.com",
        "password": "WrongPassword123!"
    }, expect_status=401)

    # 5. Forgot password
    test("POST /forgot-password", "POST", "/forgot-password", {
        "email": "testuser@demo.com"
    })

    # 6. Admin create - no key (should 403)
    test("POST /admin/create - No auth key", "POST", "/admin/create", {
        "email": "admin2@test.com",
        "password": "Adm1n@Secur3Key!",
        "full_name": "Admin User"
    }, expect_status=403)

    # 7. Admin create - wrong key (should 403)
    test("POST /admin/create - Wrong key", "POST", "/admin/create", {
        "email": "admin2@test.com",
        "password": "Adm1n@Secur3Key!",
        "full_name": "Admin User"
    }, headers={"Authorization": "AdminKey wrong-key"}, expect_status=403)

    # 8. Admin create - correct key
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret:
        test("POST /admin/create - Correct key", "POST", "/admin/create", {
            "email": "admin2@test.com",
            "password": "Adm1n@Secur3Key!",
            "full_name": "Admin User"
        }, headers={"Authorization": f"AdminKey {jwt_secret}"}, expect_status=201)
    else:
        print("\n  SKIP: JWT_SECRET_KEY not set, cannot test admin create with correct key")

    # 9. Resend OTP
    test("POST /resend-otp", "POST", "/resend-otp", {
        "email": "testuser@demo.com",
        "purpose": "signup"
    })

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS + FAIL} tests")
    print("=" * 60)

    return FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
