import requests

BASE = "http://localhost:8000/api/v1"

# Test outbreaks
print("Testing Outbreaks API...")
r = requests.get(f"{BASE}/outbreaks/all?days=60")
if r.status_code == 200:
    data = r.json()
    count = data.get('count', len(data) if isinstance(data, list) else 0)
    print(f"  Outbreaks: {count}")
    outbreaks = data.get('outbreaks', data if isinstance(data, list) else [])
    if outbreaks:
        sample = outbreaks[0]
        print(f"  Sample hospital field: {sample.get('hospital', 'NONE')}")
        print(f"  Sample city field: {sample.get('city', 'NONE')}")
        print(f"  Sample latitude: {sample.get('latitude', 'NONE')}")
else:
    print(f"  ERROR: {r.status_code} - {r.text[:200]}")

# Test hospitals
print("\nTesting Hospitals API...")
r = requests.get(f"{BASE}/hospitals/")
if r.status_code == 200:
    hospitals = r.json()
    print(f"  Hospitals: {len(hospitals)}")
    if hospitals:
        h = hospitals[0]
        print(f"  Sample: {h.get('name')} - {h.get('city')}, {h.get('state')}")
else:
    print(f"  ERROR: {r.status_code}")

# Test alerts
print("\nTesting Alerts API...")
r = requests.get(f"{BASE}/alerts/")
if r.status_code == 200:
    alerts = r.json()
    print(f"  Alerts: {len(alerts)}")
else:
    print(f"  ERROR: {r.status_code}")

# Test pending approvals count
print("\nTesting Pending Count...")
r = requests.get(f"{BASE}/outbreaks/pending-count")
if r.status_code == 200:
    print(f"  Pending: {r.json()}")
else:
    print(f"  ERROR: {r.status_code}")

# Test stats
print("\nTesting Dashboard Stats...")
r = requests.get(f"{BASE}/stats/dashboard")
if r.status_code == 200:
    stats = r.json()
    print(f"  Stats: {stats}")
else:
    print(f"  ERROR: {r.status_code}")
