import urllib.request
import json

# Check production data breakdown
url = 'https://symptomap-2-python-1.onrender.com/api/v1/outbreaks/all?days=30'

try:
    response = urllib.request.urlopen(url, timeout=60)
    data = json.loads(response.read().decode())
    
    outbreaks = data.get('outbreaks', [])
    
    # Get unique cities
    cities = {}
    for o in outbreaks:
        city = o.get('location', {}).get('city', 'Unknown')
        if city not in cities:
            cities[city] = 0
        cities[city] += 1
    
    print(f"Total outbreaks: {len(outbreaks)}")
    print(f"\nCities with zones:")
    for city, count in sorted(cities.items(), key=lambda x: -x[1]):
        print(f"  {city}: {count} zones")
        
except Exception as e:
    print(f"Error: {e}")
