import urllib.request
import urllib.error

def test_production():
    urls = [
        'https://symptomap-2-python-1.onrender.com/api/v1/outbreaks/all?days=7',
        'https://symptomap-2-python-1.onrender.com/api/v1/reports/comprehensive?days=30',
        'https://symptomap-2-python-1.onrender.com/'
    ]
    
    for url in urls:
        print(f"\nTesting: {url}")
        try:
            response = urllib.request.urlopen(url, timeout=30)
            data = response.read().decode('utf-8')
            print(f"  Status: {response.status}")
            print(f"  Data: {data[:100]}...")
        except urllib.error.HTTPError as e:
            print(f"  HTTP Error: {e.code}")
            print(f"  Body: {e.read().decode('utf-8')[:100]}")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    test_production()
