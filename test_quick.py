"""Test script for API endpoints"""
import requests

BASE = "http://localhost:8000/api/v1"

# Test outbreaks
r = requests.get(f"{BASE}/outbreaks/all?days=60")
print(f"Outbreaks: Status={r.status_code}, Count={r.json().get('count', 'N/A') if r.status_code==200 else 'ERROR'}")

# Test stats
r = requests.get(f"{BASE}/stats/dashboard")
print(f"Stats: {r.json() if r.status_code==200 else r.text}")

# Test hospitals
r = requests.get(f"{BASE}/hospitals/")
print(f"Hospitals: Count={len(r.json()) if r.status_code==200 else 'ERROR'}")

# Test auto-generate alerts
r = requests.post(f"{BASE}/alerts/generate")
print(f"Auto-alerts: {r.json() if r.status_code==200 else r.text}")

# Test alerts list
r = requests.get(f"{BASE}/alerts/")
print(f"Alerts: Count={len(r.json()) if r.status_code==200 else r.text}")
