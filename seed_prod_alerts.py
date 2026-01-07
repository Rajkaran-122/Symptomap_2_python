"""
Seed alerts to production via API
"""
import requests
import time

API_URL = "https://symptomap-2-python-1.onrender.com"

def seed_alerts():
    """Trigger the seed-alerts endpoint on production"""
    print(f"Triggering seed-alerts on {API_URL}...")
    
    # Wait a moment for backend to potentially be ready
    time.sleep(2)
    
    try:
        response = requests.post(f"{API_URL}/seed-alerts", timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def check_alerts():
    """Check if alerts exist"""
    try:
        response = requests.get(f"{API_URL}/api/v1/alerts/", timeout=30)
        data = response.json()
        print(f"Current alerts: {len(data)} alerts in database")
        return data
    except Exception as e:
        print(f"Error checking alerts: {e}")
        return []

if __name__ == "__main__":
    # First check existing alerts
    print("Checking existing alerts...")
    existing = check_alerts()
    
    if len(existing) < 20:
        print("\nSeeding more alerts...")
        result = seed_alerts()
        
    # Check again
    print("\nFinal check...")
    check_alerts()
