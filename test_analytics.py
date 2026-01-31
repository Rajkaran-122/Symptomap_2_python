import asyncio
import httpx

async def verify():
    async with httpx.AsyncClient() as client:
        base_url = "http://localhost:8000/api/v1/analytics"
        
        endpoints = [
            "/week-comparison",
            "/trend-data",
            "/severity-breakdown",
            "/disease-distribution",
            "/regional-stats"
        ]
        
        print("🔍 Verifying Analytics Endpoints...")
        
        for endpoint in endpoints:
            try:
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}: Success")
                    # specific checks
                    if endpoint == "/week-comparison":
                        print(f"   Data: {data}")
                else:
                    print(f"❌ {endpoint}: Failed ({response.status_code})")
                    print(f"   Server response: {response.text[:200]}")
            except Exception as e:
                print(f"❌ {endpoint}: Error ({str(e)})")

if __name__ == "__main__":
    asyncio.run(verify())
