import requests
import json

try:
    r = requests.get('http://localhost:8000/api/v1/outbreaks/all')
    print(f"Status: {r.status_code}")
    data = r.json()
    outbreaks = data.get('outbreaks', [])
    print(f"Outbreaks count: {len(outbreaks)}")
    if len(outbreaks) > 0:
        print("First outbreak:", outbreaks[0])
except Exception as e:
    print(f"Error: {e}")
