"""
Check alerts on production
"""
import urllib.request
import json

API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

def get_doctor_token():
    url = f"{API_URL}/doctor/login"
    data = json.dumps({"password": "Doctor@SymptoMap2025"}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(req, timeout=30)
    return json.loads(response.read().decode()).get('access_token')

def main():
    token = get_doctor_token()
    print(f"Token obtained")
    
    # Check submissions endpoint
    req = urllib.request.Request(f"{API_URL}/doctor/submissions")
    req.add_header('Authorization', f'Bearer {token}')
    data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    
    print(f"\nTotal Alerts: {data.get('total_alerts', 0)}")
    print(f"Total Outbreaks: {data.get('total_outbreaks', 0)}")
    
    alerts = data.get('alerts', [])
    if alerts:
        print(f"\nSample alerts:")
        for i, a in enumerate(alerts[:5]):
            print(f"  {i+1}. [{a.get('alert_type', 'unknown')}] {a.get('title', 'untitled')[:50]}")

if __name__ == "__main__":
    main()
