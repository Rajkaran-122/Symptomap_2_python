
import requests
import json
from datetime import datetime

# URL = "https://symptomap-2-python-1.onrender.com/api/v1"
URL = "https://symptomap-2-python-1.onrender.com/api/v1"

# Use admin to check pending (Doctor station might only show own?)
EMAIL = "admin@symptomap.com"
PASSWORD = "admin123"

def check_pending():
    print(f"🔍 Diagnosing Pending Approvals at {URL}...")
    
    # Login
    sess = requests.Session()
    try:
        resp = sess.post(f"{URL}/auth/login", data={"username": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"❌ Login failed: {resp.status_code}")
            return
        token = resp.json()["access_token"]
        sess.headers["Authorization"] = f"Bearer {token}"
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # Get Pending (Admin endpoint usually /admin/outbreaks?status=pending or similar)
    # But let's try the doctor station endpoint too if admin fails, or the general listing
    # Based on file list, endpoints might be /outbreaks/pending or /doctor/outbreaks
    
    print("Checking /doctor/outbreaks (pending)...")
    try:
        # Assuming there is a way to filter or list. 
        # Let's try to get ALL outbreaks and filter client side if needed, 
        # or use a known pending endpoint.
        # Looking at previous logs, `seed_production.py` used `/api/v1/admin/pending`
        
        resp = sess.get(f"{URL}/admin/pending")
        if resp.status_code == 200:
            pending = resp.json()
            print(f"📊 Count from /admin/pending: {len(pending)}")
            if len(pending) > 0:
                print("First 5 dates:")
                for p in pending[:5]:
                    print(f" - ID: {p.get('id')} | Reported: {p.get('date_reported')} | Created: {p.get('created_at')}")
        else:
            print(f"⚠️ /admin/pending failed: {resp.status_code}")
            
            # Try doctor endpoint
            resp = sess.get(f"{URL}/doctor/outbreaks") # lists doctor's submissions
            if resp.status_code == 200:
                 data = resp.json()
                 # Count pending
                 pending_doc = [x for x in data if x.get('status') == 'pending']
                 print(f"📊 Count from /doctor/outbreaks (My Submissions): {len(pending_doc)}")
            else:
                print(f"⚠️ /doctor/outbreaks failed: {resp.status_code}")

    except Exception as e:
        print(f"❌ Error fetching data: {e}")

if __name__ == "__main__":
    check_pending()
