import requests

def trigger_force_seed():
    url = "https://symptomap-2-python-1.onrender.com/force-seed"
    # url = "http://localhost:8000/force-seed"
    
    print(f"Triggering force-seed at {url}...")
    try:
        response = requests.post(url, timeout=300) # Long timeout for seeding
        if response.status_code == 200:
            print("✅ Force seed successful:")
            print(response.json())
        else:
            print(f"❌ Force seed failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    trigger_force_seed()
