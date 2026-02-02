"""
Comprehensive API Feature Test Script
Tests all endpoints and features to identify errors
"""
import asyncio
import httpx
import json
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"
RESULTS = {"passed": [], "failed": []}

async def test_endpoint(client, name, method, path, expected_status=200, **kwargs):
    try:
        if method == "GET":
            r = await client.get(f"{API_URL}{path}", **kwargs)
        elif method == "POST":
            r = await client.post(f"{API_URL}{path}", **kwargs)
        else:
            r = await client.request(method, f"{API_URL}{path}", **kwargs)
        
        if r.status_code == expected_status:
            RESULTS["passed"].append({"name": name, "status": r.status_code})
            print(f"✅ {name}: {r.status_code}")
            return r.json() if r.status_code == 200 else None
        else:
            RESULTS["failed"].append({"name": name, "status": r.status_code, "error": r.text[:200]})
            print(f"❌ {name}: {r.status_code} - {r.text[:100]}")
            return None
    except Exception as e:
        RESULTS["failed"].append({"name": name, "status": "ERR", "error": str(e)})
        print(f"❌ {name}: Exception - {str(e)[:100]}")
        return None

async def run_all_tests():
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE FEATURE TEST")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # ========== PUBLIC ENDPOINTS ==========
        print("\n📌 PUBLIC ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Health Check", "GET", "/health")
        await test_endpoint(client, "Outbreaks List", "GET", "/outbreaks/")
        await test_endpoint(client, "Outbreaks All", "GET", "/outbreaks/all?days=30")
        await test_endpoint(client, "Outbreaks GeoJSON", "GET", "/outbreaks/geojson")
        await test_endpoint(client, "Pending Count", "GET", "/outbreaks/pending-count")
        
        # ========== STATS ENDPOINTS ==========
        print("\n📌 STATS ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Dashboard Stats", "GET", "/stats/dashboard")
        await test_endpoint(client, "Performance Metrics", "GET", "/stats/performance")
        await test_endpoint(client, "Risk Zones", "GET", "/stats/zones")
        await test_endpoint(client, "Analytics Data", "GET", "/stats/analytics")
        
        # ========== ANALYTICS ENDPOINTS ==========
        print("\n📌 ANALYTICS ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Activity Feed", "GET", "/analytics/activity-feed")
        await test_endpoint(client, "Trend Data", "GET", "/analytics/trend-data")
        await test_endpoint(client, "Disease Distribution", "GET", "/analytics/disease-distribution")
        await test_endpoint(client, "Severity Breakdown", "GET", "/analytics/severity-breakdown")
        await test_endpoint(client, "Regional Stats", "GET", "/analytics/regional-stats")
        await test_endpoint(client, "Week Comparison", "GET", "/analytics/week-comparison")
        
        # ========== ALERTS ENDPOINTS ==========
        print("\n📌 ALERTS ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Alerts List", "GET", "/alerts/")
        await test_endpoint(client, "Active Alerts", "GET", "/alerts/active")
        
        # ========== PREDICTIONS ENDPOINTS ==========
        print("\n📌 PREDICTIONS ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Predictions List", "GET", "/predictions/")
        await test_endpoint(client, "Predictions Enhanced", "GET", "/predictions/enhanced")
        await test_endpoint(client, "AI Chat", "POST", "/predictions/chat", json={"message": "test"})
        
        # ========== HOSPITALS ENDPOINTS ==========
        print("\n📌 HOSPITALS ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Hospitals List", "GET", "/hospitals/")
        await test_endpoint(client, "Hospitals GeoJSON", "GET", "/hospitals/geojson")
        
        # ========== AUTH ENDPOINTS (PUBLIC) ==========
        print("\n📌 AUTH ENDPOINTS")
        print("-"*40)
        
        await test_endpoint(client, "Auth Login (NoCredentials)", "POST", "/auth/login", 
                          expected_status=422, data={"username": "", "password": ""})
        
        # ========== ADMIN ENDPOINTS (May need auth) ==========
        print("\n📌 ADMIN ENDPOINTS (Testing without auth)")
        print("-"*40)
        
        await test_endpoint(client, "Admin Pending Approvals", "GET", "/admin/pending-approvals")
        await test_endpoint(client, "Admin All Outbreaks", "GET", "/admin/outbreaks")
        
        # ========== DOCTOR ENDPOINTS (Need auth) ==========
        print("\n📌 DOCTOR ENDPOINTS (Testing without auth)")
        print("-"*40)
        
        r = await test_endpoint(client, "Doctor Stats (NoAuth)", "GET", "/doctor/stats", expected_status=401)
        r = await test_endpoint(client, "Doctor Submissions (NoAuth)", "GET", "/doctor/submissions", expected_status=401)
        
    # ========== SUMMARY ==========
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {len(RESULTS['passed'])}")
    print(f"❌ Failed: {len(RESULTS['failed'])}")
    
    if RESULTS["failed"]:
        print("\n🔴 FAILED TESTS:")
        for f in RESULTS["failed"]:
            print(f"   - {f['name']}: {f['status']} - {f.get('error', '')[:80]}")
    
    return RESULTS

if __name__ == "__main__":
    asyncio.run(run_all_tests())
