import requests
import json

def check_data():
    url = "https://symptomap-2-python-1.onrender.com/api/v1/outbreaks"
    try:
        response = requests.get(url, params={"limit": 10}, timeout=10)
        data = response.json()
        
        print(f"Fetched {len(data)} outbreaks.")
        valid_count = 0
        zero_count = 0
        
        for ob in data:
            loc = ob.get("location", {})
            lat = loc.get("latitude") or loc.get("lat")
            lng = loc.get("longitude") or loc.get("lng")
            
            print(f"ID: {ob.get('id')} | City: {ob.get('city')} | Lat: {lat}, Lng: {lng}")
            
            if lat == 0 and lng == 0:
                zero_count += 1
            elif lat is not None and lng is not None:
                valid_count += 1
                
        print(f"\nSummary:")
        print(f"✅ Valid coordinates: {valid_count}")
        print(f"❌ Zero coordinates: {zero_count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()
