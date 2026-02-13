"""Quick OTP endpoint tests - writes results to test_output.txt"""
import urllib.request, json, os

results = []

def test(name, method, path, data=None, headers=None, expect_status=200):
    url = "http://localhost:8000/api/v1/auth/otp" + path
    try:
        body = json.dumps(data).encode("utf-8") if data else None
        h = {"Content-Type": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        r = urllib.request.urlopen(req)
        result = json.loads(r.read().decode("utf-8"))
        status = r.status
    except urllib.error.HTTPError as e:
        result = json.loads(e.read().decode("utf-8"))
        status = e.code
    except Exception as e:
        result = {"error": str(e)}
        status = 0

    passed = status == expect_status
    line = f"{'PASS' if passed else 'FAIL'} | {name} | {status} (expect {expect_status}) | {json.dumps(result)}"
    results.append(line)
    return result, status

import random
rnd = random.randint(1000, 9999)
email = f"test{rnd}@demo.com"
admin_email = f"admin{rnd}@test.com"

test("Status check", "GET", "/status")
test("Signup user", "POST", "/signup", {"email":email,"phone":f"+91{rnd}000000","password":"MyStr0ng@Pass!","full_name":"Test","role":"user"}, expect_status=201)
test("Login user (unverified)", "POST", "/login", {"email":email,"password":"MyStr0ng@Pass!"}, expect_status=403)
test("Login wrong pass", "POST", "/login", {"email":email,"password":"WrongPass123!!!"}, expect_status=401)
test("Forgot password", "POST", "/forgot-password", {"email":email})
test("Admin no key", "POST", "/admin/create", {"email":admin_email,"password":"Adm1n@Secur3Key!","full_name":"A"}, expect_status=403)
test("Admin wrong key", "POST", "/admin/create", {"email":admin_email,"password":"Adm1n@Secur3Key!","full_name":"A"}, headers={"Authorization":"AdminKey wrong"}, expect_status=403)
test("Resend OTP", "POST", "/resend-otp", {"email":email,"purpose":"signup"})

with open("test_output.txt", "w", encoding="utf-8") as f:
    for line in results:
        f.write(line + "\n")
    total = len(results)
    passed = sum(1 for l in results if l.startswith("PASS"))
    f.write(f"\nRESULTS: {passed}/{total} passed\n")

print(f"Done. {sum(1 for l in results if l.startswith('PASS'))}/{len(results)} passed")
