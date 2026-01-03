import urllib.request
import urllib.error
import json

def trigger_production_seed():
    """Trigger the /seed endpoint on production to populate data"""
    
    url = 'https://symptomap-2-python-1.onrender.com/seed'
    
    print(f"🚀 Triggering seed on production...")
    print(f"   URL: {url}")
    
    try:
        # POST request to trigger seeding
        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        response = urllib.request.urlopen(req, timeout=60)
        data = response.read().decode('utf-8')
        
        print(f"\n✅ Success! Status: {response.status}")
        print(f"   Response: {data}")
        
        return json.loads(data)
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error: {e.code}")
        print(f"   Body: {e.read().decode('utf-8')[:500]}")
        return None
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None

if __name__ == "__main__":
    result = trigger_production_seed()
    
    if result and result.get('status') == 'success':
        print("\n🎉 Production database seeded successfully!")
        print("   Refresh the dashboard to see 173 zones")
    else:
        print("\n⚠️ Seeding may have failed - check Render logs")
