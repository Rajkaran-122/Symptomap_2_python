
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.api.v1.auth import get_admin_user
import time
import os
import psutil
from datetime import datetime, timezone

router = APIRouter(prefix="/health", tags=["Monitoring"])

# Store startup time
START_TIME = time.time()

@router.get("/live")
async def liveness_probe():
    """
    Liveness probe: Returns 200 if the service is running.
    Used by load balancers to determine if the pod/container is alive.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe: Returns 200 if the service is ready to accept traffic.
    Checks database connectivity.
    """
    try:
        # Check DB connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )

@router.get("/metrics")
async def system_metrics(current_user: dict = Depends(get_admin_user)):
    """
    Get system metrics (Admin/Doctor only).
    """
    process = psutil.Process(os.getpid())
    uptime_seconds = time.time() - START_TIME
    
    return {
        "status": "ok",
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_display": str(timedelta(seconds=int(uptime_seconds))),
        "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
        "cpu_percent": process.cpu_percent(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

from datetime import timedelta
