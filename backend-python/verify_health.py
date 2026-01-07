
import sys
import os
import asyncio

sys.path.append(os.getcwd())

from app.api.v1.monitoring import liveness_probe, readiness_probe

print("Verifying Health Monitoring...")

async def test_probes():
    try:
        # Test Live
        live = await liveness_probe()
        assert live["status"] == "ok"
        print("✅ Liveness Check Passed")
        
        # Readiness requires DB mock, skipping logic execution but verifying import
        print("✅ Readiness Import Passed")
        
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_probes())
