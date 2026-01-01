"""
Public API endpoint to get all outbreaks including approved doctor submissions
Combines data from both doctor_outbreaks (approved only) and regular outbreaks tables
"""

from fastapi import APIRouter
from typing import List, Dict
import sqlite3
import os
from datetime import datetime, timezone
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/outbreaks", tags=["Public Outbreaks"])


def get_db_connection():
    """Get SQLite database connection"""
    # Use correct path relative to app location
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'symptomap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/all")
async def get_all_outbreaks():
    """
    Get all outbreaks from both APPROVED doctor submissions and regular outbreaks
    """
    try:
        # DB Path calculation
        # Go up: v1 -> api -> app -> backend-python -> symptomap.db
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        db_path = os.path.join(base_dir, 'symptomap.db')
        
        if not os.path.exists(db_path):
            # Fallback for different environments
            db_path = os.path.join(os.getcwd(), 'backend-python', 'symptomap.db')
            if not os.path.exists(db_path):
                # Another fallback
                db_path = os.path.join(os.getcwd(), 'symptomap.db')

        outbreaks = []
        alerts = []
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Fetch Approved Outbreaks
        try:
            cursor.execute('''
                SELECT id, disease_type, patient_count, severity, latitude, longitude,
                       location_name, city, state, description, date_reported, created_at, status
                FROM doctor_outbreaks
                WHERE status = 'approved'
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            for row in rows:
                outbreaks.append({
                    "id": f"doc_{row['id']}",
                    "disease": str(row['disease_type']),
                    "cases": int(row['patient_count']),
                    "severity": str(row['severity']),
                    "location": {
                        "name": str(row['location_name']) if row['location_name'] else "",
                        "city": str(row['city']) if row['city'] else "",
                        "state": str(row['state']) if row['state'] else "",
                        "latitude": float(row['latitude']) if row['latitude'] else 0.0,
                        "longitude": float(row['longitude']) if row['longitude'] else 0.0
                    },
                    "description": str(row['description']) if row['description'] else "",
                    "reported_date": str(row['date_reported']) if row['date_reported'] else str(row['created_at']),
                    "source": "Doctor Submission (Approved)",
                    "status": "approved",
                    "verified": True
                })
        except Exception as e:
            print(f"Error fetching outbreaks: {e}")
            # Continue to alerts
            
        # 2. Fetch Active Alerts
        try:
            cursor.execute('''
                SELECT id, alert_type, title, message, latitude, longitude,
                       affected_area, expiry_date, created_at, status
                FROM doctor_alerts
                WHERE status = 'active'
            ''')
            rows = cursor.fetchall()
            for row in rows:
                alerts.append({
                    "id": f"alert_{row['id']}",
                    "type": str(row['alert_type']),
                    "title": str(row['title']),
                    "message": str(row['message']),
                    "location": {
                        "latitude": float(row['latitude']) if row['latitude'] else 0.0,
                        "longitude": float(row['longitude']) if row['longitude'] else 0.0,
                        "area": str(row['affected_area']) if row['affected_area'] else ""
                    },
                    "expiry": str(row['expiry_date']) if row['expiry_date'] else "",
                    "created": str(row['created_at']) if row['created_at'] else "",
                    "status": str(row['status'])
                })
        except Exception as e:
            print(f"Error fetching alerts: {e}")

        conn.close()
        
        return JSONResponse(content={
            "outbreaks": outbreaks,
            "alerts": alerts,
            "total_outbreaks": len(outbreaks),
            "total_alerts": len(alerts),
            "last_updated": datetime.now(timezone.utc).isoformat()
        })

    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=200, # Return 200 so frontend handles it gently? No, debugging.
            content={
                "error": str(e),
                "traceback": traceback.format_exc(),
                "db_path_attempted": db_path if 'db_path' in locals() else "unknown"
            }
        )


@router.get("/pending-count")
async def get_pending_count():
    """Get count of pending submissions for notification badge"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending' OR status IS NULL")
        row = cursor.fetchone()
        count = row[0] if row else 0
        conn.close()
        return {"pending_count": count}
    except:
        return {"pending_count": 0}
