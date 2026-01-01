
import requests
import json

try:
    print("Testing /outbreaks/all Endpoint...")
    r = requests.get('http://localhost:8000/api/v1/outbreaks/all')
    print(f"Status: {r.status_code}")
    print("Content:")
    try:
        print(json.dumps(r.json(), indent=2))
    except:
        print(r.text)
except Exception as e:
    print(f"Failed: {e}")
