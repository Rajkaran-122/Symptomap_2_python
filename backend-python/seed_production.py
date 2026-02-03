#!/usr/bin/env python3
"""
Production Database Seeder for SymptoMap
Run this script to populate the production database with comprehensive data.

Usage:
    python seed_production.py

Or call the API endpoints:
    POST /force-seed     - Seeds outbreaks and hospitals
    POST /seed-alerts    - Seeds alerts
"""

import requests
import sys
from datetime import datetime

# Production API URL
PRODUCTION_URL = "https://symptomap-2-python-1.onrender.com"

def seed_production():
    """Seed the production database with comprehensive data"""
    
    print("=" * 60)
    print("SymptoMap Production Database Seeder")
    print("=" * 60)
    print(f"Target: {PRODUCTION_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Step 1: Health check
    print("1. Checking API health...")
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=60)
        if response.status_code == 200:
            print("   ✅ API is healthy")
        else:
            print(f"   ⚠️ Health check returned {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        print("   Note: Render may be waking up. Waiting 30 seconds...")
        import time
        time.sleep(30)
    
    # Step 2: Force seed database
    print("\n2. Seeding database with comprehensive data...")
    try:
        response = requests.post(f"{PRODUCTION_URL}/force-seed", timeout=120)
        result = response.json()
        if result.get("status") == "success":
            print(f"   ✅ {result.get('message')}")
        else:
            print(f"   ⚠️ Seed result: {result}")
    except Exception as e:
        print(f"   ❌ Force seed failed: {e}")
    
    # Step 3: Seed alerts
    print("\n3. Seeding alerts for Alert Management...")
    try:
        response = requests.post(f"{PRODUCTION_URL}/seed-alerts", timeout=60)
        result = response.json()
        if result.get("status") == "success":
            print(f"   ✅ {result.get('message')}")
        else:
            print(f"   ⚠️ Alert seed result: {result}")
    except Exception as e:
        print(f"   ❌ Alert seed failed: {e}")
    
    # Step 4: Verify data
    print("\n4. Verifying seeded data...")
    try:
        # Check stats
        response = requests.get(f"{PRODUCTION_URL}/api/v1/stats/dashboard", timeout=30)
        stats = response.json()
        print(f"   📊 Active Outbreaks: {stats.get('active_outbreaks', 'N/A')}")
        print(f"   🏥 Hospitals Monitored: {stats.get('hospitals_monitored', 'N/A')}")
        print(f"   🤖 AI Predictions: {stats.get('ai_predictions', 'N/A')}")
        print(f"   🗺️ Coverage: {stats.get('coverage_area', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️ Could not verify stats: {e}")
    
    try:
        # Check alerts
        response = requests.get(f"{PRODUCTION_URL}/api/v1/alerts/", timeout=30)
        alerts = response.json()
        print(f"   🔔 Total Alerts: {len(alerts) if isinstance(alerts, list) else 'N/A'}")
    except Exception as e:
        print(f"   ⚠️ Could not verify alerts: {e}")
    
    try:
        # Check zones
        response = requests.get(f"{PRODUCTION_URL}/api/v1/stats/zones", timeout=30)
        zones = response.json()
        print(f"   ⚠️ High Risk Zones: {zones.get('high_risk_zones', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️ Could not verify zones: {e}")
    
    print("\n" + "=" * 60)
    print("Seeding complete! Please verify on the dashboard:")
    print(f"  https://symptomap-2-python.vercel.app/dashboard")
    print("=" * 60)


def test_auth():
    """Test authentication flow"""
    print("\n5. Testing authentication...")
    
    try:
        # Test login
        response = requests.post(
            f"{PRODUCTION_URL}/api/v1/auth/login",
            data={
                "username": "admin@symptomap.com",
                "password": "Admin@SymptoMap2025"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Admin login successful")
            print(f"   👤 User: {data['user']['full_name']} ({data['user']['role']})")
            return data['access_token']
        else:
            print(f"   ❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Auth test failed: {e}")
        return None


def test_protected_endpoints(token):
    """Test protected endpoints with auth token"""
    if not token:
        print("\n6. Skipping protected endpoint tests (no token)")
        return
    
    print("\n6. Testing protected endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test doctor stats
    try:
        response = requests.get(
            f"{PRODUCTION_URL}/api/v1/doctor/stats",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Doctor stats: {stats}")
        else:
            print(f"   ⚠️ Doctor stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Doctor stats error: {e}")
    
    # Test admin pending
    try:
        response = requests.get(
            f"{PRODUCTION_URL}/api/v1/admin/pending",
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            pending = response.json()
            print(f"   ✅ Admin pending: {len(pending)} items")
        elif response.status_code == 403:
            print(f"   ℹ️ Admin pending: Admin role required")
        else:
            print(f"   ⚠️ Admin pending: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin pending error: {e}")


if __name__ == "__main__":
    seed_production()
    token = test_auth()
    test_protected_endpoints(token)
