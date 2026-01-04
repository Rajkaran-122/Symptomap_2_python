"""
Check if the approval page endpoint is working
"""

import urllib.request
import json

API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

def get_doctor_token():
    """Login and get doctor token"""
    url = f"{API_URL}/doctor/login"
    data = json.dumps({"password": "Doctor@SymptoMap2025"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        return result.get('access_token')
    except Exception as e:
        print(f"Login error: {e}")
        return None

def check_pending_requests(token):
    """Get all pending requests"""
    url = f"{API_URL}/admin/pending"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=60)
        data = json.loads(response.read().decode())
        return data
    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode()[:500]}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("🔐 Getting doctor token...")
    token = get_doctor_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Token obtained")
    
    print("\n📋 Checking pending requests on production...")
    pending = check_pending_requests(token)
    
    if pending is None:
        print("❌ Failed to get pending requests")
        return
    
    print(f"\n✅ Found {len(pending)} pending approval requests!")
    
    # Show first 10
    print("\n📝 Sample pending requests:")
    for i, req in enumerate(pending[:10]):
        city = req.get('city', 'Unknown')
        state = req.get('state', 'Unknown')
        disease = req.get('disease_type', 'Unknown')
        severity = req.get('severity', 'unknown')
        patients = req.get('patient_count', 0)
        hospital = req.get('location_name', 'Unknown')
        
        print(f"  {i+1}. {city}, {state} - {disease} ({severity}) - {patients} patients - {hospital}")
    
    print(f"\n...and {len(pending) - 10} more requests")
    
    print(f"\n📋 Visit Approval Page:")
    print(f"   https://symptomap-2-python.vercel.app/admin/approvals")

if __name__ == "__main__":
    main()
