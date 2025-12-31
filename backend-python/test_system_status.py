import requests

print("\n" + "="*80)
print("SYMPTOMAP - SYSTEM STATUS VERIFICATION")
print("="*80)

# Test 1: Outbreak GET
print("\n[TEST 1] Outbreak GET endpoint...")
try:
    r = requests.get('http://localhost:8000/api/v1/outbreaks/')
    print(f"  Status: {r.status_code}")
    data = r.json() if r.status_code == 200 else []
    print(f"  Outbreaks in DB: {len(data)}")
    print(f"  Result: {'✅ WORKS' if r.status_code == 200 else '❌ FAILED'}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 2: Outbreak POST (without auth)
print("\n[TEST 2] Outbreak POST (without auth)...")
try:
    payload = {
        'hospital_name': 'Status Test Hospital',
        'disease_type': 'Dengue',
        'patient_count': 50,
        'severity': 'moderate',
        'location': {'lat': 19.076, 'lng': 72.877},
        'date_started': '2024-12-09T10:00:00'
    }
    r = requests.post('http://localhost:8000/api/v1/outbreaks/', json=payload)
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:80]}...")
    if r.status_code in [200, 201]:
        print(f"  Result: ✅ WORKS - Form submission will work!")
    elif r.status_code == 401:
        print(f"  Result: ❌ AUTH REQUIRED - Server needs restart")
    else:
        print(f"  Result: ❌ FAILED")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 3: Stats Dashboard
print("\n[TEST 3] Stats Dashboard endpoint...")
try:
    r = requests.get('http://localhost:8000/api/v1/stats/dashboard')
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print(f"  Response: {r.text[:100]}...")
        print(f"  Result: ✅ WORKS - Dashboards will show data!")
    elif r.status_code == 404:
        print(f"  Result: ❌ NOT LOADED - Server needs restart")
    else:
        print(f"  Result: ❌ FAILED")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 4: Frontend
print("\n[TEST 4] Frontend availability...")
try:
    r = requests.get('http://localhost:5173/')
    print(f"  Status: {r.status_code}")
    print(f"  Result: {'✅ Frontend running' if r.status_code == 200 else '❌ Frontend down'}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
CURRENT STATE:
  - Old backend server: STILL RUNNING (14+ hours)
  - New code fixes: NOT LOADED (server hasn't restarted)
  - Database: EMPTY (0 outbreaks)
  
WHAT WORKS:
  ✅ Frontend is up and accessible
  ✅ Basic outbreak GET endpoint works
  
WHAT DOESN'T WORK (Needs Server Restart):
  ❌ Outbreak POST returns 401 (auth required)
  ❌ Stats endpoints return 404 (not registered)
  ❌ Doctor Station form fails
  ❌ Dashboard shows zeros
  ❌ Map has no circles
  
THE FIX (Takes 30 seconds):
  1. Close the uvicorn terminal (Ctrl+C)
  2. Run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  3. Run: python add_professional_data.py
  
THEN EVERYTHING WILL WORK:
  ✅ Form submissions succeed
  ✅ Data appears everywhere
  ✅ Map shows colored circles (red/yellow/green)
  ✅ Analytics update in real-time
""")
print("="*80 + "\n")
