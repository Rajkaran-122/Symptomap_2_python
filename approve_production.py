"""
Approve all pending doctor outbreaks on production
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

def get_pending_requests(token):
    """Get all pending requests"""
    url = f"{API_URL}/admin/pending"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=60)
        return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error getting pending: {e}")
        return []

def approve_request(token, request_id):
    """Approve a single request"""
    url = f"{API_URL}/admin/approve/{request_id}"
    
    req = urllib.request.Request(url, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Error approving {request_id}: {e}")
        return False

def main():
    print("🔐 Getting doctor token...")
    token = get_doctor_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Token obtained")
    
    print("\n📋 Getting pending requests...")
    pending = get_pending_requests(token)
    
    if not pending:
        print("   No pending requests found")
        return
    
    print(f"   Found {len(pending)} pending requests")
    
    success_count = 0
    for req in pending:
        req_id = req.get('id')
        city = req.get('city', 'Unknown')
        disease = req.get('disease_type', 'Unknown')
        
        if approve_request(token, req_id):
            success_count += 1
            print(f"  ✅ Approved: {city} - {disease}")
        else:
            print(f"  ❌ Failed: {city}")
    
    print(f"\n🎉 Successfully approved {success_count}/{len(pending)} requests!")
    print(f"\n🔄 Refresh the dashboard to see all zones!")

if __name__ == "__main__":
    main()
