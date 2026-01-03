"""
Debug the reports endpoint locally
"""
import urllib.request
import json

# Test the reports endpoint
url = 'http://localhost:8000/api/v1/reports/comprehensive?days=30'

print("Testing reports endpoint...")
try:
    response = urllib.request.urlopen(url, timeout=30)
    data = json.loads(response.read().decode())
    
    print(f"\nFull Response:")
    print(json.dumps(data, indent=2))
    
except Exception as e:
    print(f"Error: {e}")
