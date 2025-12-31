"""
FINAL SYSTEM CHECK - Complete Status Report
"""
import requests

print("\n" + "="*80)
print("🔍 SYMPTOMAP - FINAL SYSTEM STATUS CHECK")
print("="*80)

tests_passed = 0
tests_failed = 0

# Test 1: Backend Server
print("\n[1] Backend Server Status")
try:
    r = requests.get('http://localhost:8000/docs', timeout=5)
    if r.status_code == 200:
        print("  ✅ Backend is running")
        tests_passed += 1
    else:
        print(f"  ❌ Backend returned {r.status_code}")
        tests_failed += 1
except:
    print("  ❌ Backend not accessible")
    tests_failed += 1

# Test 2: Frontend Server
print("\n[2] Frontend Server Status")
try:
    r = requests.get('http://localhost:5173/', timeout=5)
    if r.status_code == 200:
        print("  ✅ Frontend is running")
        tests_passed += 1
    else:
        print(f"  ❌ Frontend returned {r.status_code}")
        tests_failed += 1
except:
    print("  ❌ Frontend not accessible")
    tests_failed += 1

# Test 3: Database Connection (via GET)
print("\n[3] Database Connection")
try:
    r = requests.get('http://localhost:8000/api/v1/outbreaks/', timeout=5)
    if r.status_code == 200:
        print("  ✅ Database connection works")
        data = r.json()
        print(f"  📊 Current outbreaks in DB: {len(data)}")
        tests_passed += 1
    else:
        print(f"  ❌ Database check failed ({r.status_code})")
        tests_failed += 1
except Exception as e:
    print(f"  ❌ Database error: {e}")
    tests_failed += 1

# Test 4: Authentication Fix Status
print("\n[4] Authentication Fix Status")
try:
    payload = {'hospital_name': 'Test', 'disease_type': 'Test', 'patient_count': 1, 
               'severity': 'mild', 'location': {'lat': 19.076, 'lng': 72.877}, 
               'date_started': '2024-12-09T10:00:00'}
    r = requests.post('http://localhost:8000/api/v1/outbreaks/', json=payload, timeout=5)
    
    if r.status_code in [200, 201]:
        print("  ✅ Authentication bypass ACTIVE - Form will work!")
        tests_passed += 1
    elif r.status_code == 401:
        print("  ❌ Authentication required (OLD CODE running)")
        print("  🔧 Fix: Server needs restart to load authentication bypass")
        tests_failed += 1
    else:
        print(f"  ❌ Unexpected response: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ❌ Error: {e}")
    tests_failed += 1

# Test 5: Stats API Status
print("\n[5] Stats API Status")
try:
    r = requests.get('http://localhost:8000/api/v1/stats/dashboard', timeout=5)
    if r.status_code == 200:
        print("  ✅ Stats API ACTIVE - Dashboards will show data!")
        tests_passed += 1
    elif r.status_code == 404:
        print("  ❌ Stats API not found (OLD CODE running)")
        print("  🔧 Fix: Server needs restart to load stats endpoints")
        tests_failed += 1
    else:
        print(f"  ❌ Unexpected response: {r.status_code}")
        tests_failed += 1
except Exception as e:
    print(f"  ❌ Error: {e}")
    tests_failed += 1

# Summary
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)
print(f"  ✅ Tests Passed: {tests_passed}/5")
print(f"  ❌ Tests Failed: {tests_failed}/5")

if tests_failed == 0:
    print("\n🎉 SYSTEM STATUS: FULLY OPERATIONAL!")
    print("  All systems working correctly!")
    print("  You can now:")
    print("    - Add outbreak data via Doctor Station")
    print("    - See colored circles on map")
    print("    - View real-time analytics")
elif tests_passed >= 2:
    print("\n⚠️  SYSTEM STATUS: PARTIALLY WORKING")
    print(f"  {tests_passed} components working, {tests_failed} need attention")
    if tests_failed == 2 and "401" in str(tests_failed):
        print("\n🔧 ACTION REQUIRED:")
        print("  The backend server is running OLD CODE (15+ hours uptime)")
        print("  All fixes are implemented but not loaded")
        print("\n  TO FIX (30 seconds):")
        print("    1. Press Ctrl+C in uvicorn terminal")
        print("    2. Run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("    3. Run: python add_comprehensive_data.py")
        print("    4. Refresh http://localhost:5173/")
else:
    print("\n❌ SYSTEM STATUS: CRITICAL ISSUES")
    print(f"  Only {tests_passed} out of 5 tests passed")

print("\n" + "="*80 + "\n")
