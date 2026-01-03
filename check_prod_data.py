import urllib.request
import json

def check_production_data():
    """Check what data exists on production"""
    
    endpoints = [
        'https://symptomap-2-python-1.onrender.com/api/v1/outbreaks/all?days=30',
        'https://symptomap-2-python-1.onrender.com/api/v1/reports/comprehensive?days=30'
    ]
    
    for url in endpoints:
        print(f"\n🔍 Testing: {url.split('/')[-1].split('?')[0]}")
        try:
            response = urllib.request.urlopen(url, timeout=60)
            data = json.loads(response.read().decode())
            
            if 'outbreaks' in data:
                print(f"   Outbreaks count: {len(data['outbreaks'])}")
                if data['outbreaks']:
                    sample = data['outbreaks'][0]
                    print(f"   Sample: {sample.get('disease', 'N/A')} in {sample.get('location', {}).get('name', 'N/A')}")
            elif 'summary' in data:
                summary = data['summary']
                print(f"   Total Outbreaks: {summary.get('outbreaks', {}).get('total', 0)}")
                print(f"   Total Patients: {summary.get('outbreaks', {}).get('total_patients', 0)}")
                print(f"   Total Alerts: {summary.get('alerts', {}).get('total', 0)}")
                print(f"   Affected Hospitals: {summary.get('hospitals', {}).get('affected', 0)}")
            else:
                print(f"   Response: {str(data)[:200]}")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    check_production_data()
