"""
Admin Approval API Endpoints
Allows admins to review, approve, or reject doctor submissions
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
from app.api.v1.auth_doctor import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.outbreak import Outbreak, Hospital
from app.core.audit import log_audit_event
from fastapi import Request
import sqlite3

router = APIRouter(prefix="/admin", tags=["Admin Approval"])


class PendingRequest(BaseModel):
    id: int
    disease_type: str
    patient_count: int
    severity: str
    latitude: float
    longitude: float
    location_name: str
    city: str
    state: str
    description: Optional[str]
    date_reported: str
    submitted_by: str
    created_at: str
    status: str


class ApprovalResponse(BaseModel):
    success: bool
    message: str
    outbreak_id: Optional[str] = None


def get_sqlite_connection():
    """Get SQLite database connection"""
    from app.core.config import get_sqlite_db_path
    conn = sqlite3.connect(get_sqlite_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def ensure_status_column():
    """Ensure status column exists in doctor_outbreaks table"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    # Ensure table exists first (Robustness fix)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_outbreaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_type TEXT,
            patient_count INTEGER,
            severity TEXT,
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            city TEXT,
            state TEXT,
            description TEXT,
            date_reported TEXT,
            submitted_by TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Check if status column exists
    cursor.execute("PRAGMA table_info(doctor_outbreaks)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'status' not in columns:
        cursor.execute("ALTER TABLE doctor_outbreaks ADD COLUMN status TEXT DEFAULT 'pending'")
        conn.commit()
    
    conn.commit()  # Ensure table creation is committed
    conn.close()


@router.get("/pending", response_model=List[PendingRequest])
async def get_pending_requests(payload: dict = Depends(verify_token)):
    """
    Get all pending doctor submissions awaiting approval
    
    Requires authentication.
    """
    
    ensure_status_column()
    
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM doctor_outbreaks 
            WHERE status = 'pending' OR status IS NULL
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        pending = []
        for row in rows:
            pending.append(PendingRequest(
                id=row['id'],
                disease_type=row['disease_type'],
                patient_count=row['patient_count'],
                severity=row['severity'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                location_name=row['location_name'] or '',
                city=row['city'] or '',
                state=row['state'] or '',
                description=row['description'] or '',
                date_reported=row['date_reported'] or '',
                submitted_by=row['submitted_by'] or 'doctor',
                created_at=row['created_at'] or '',
                status=row['status'] or 'pending'
            ))
        
        return pending
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")


@router.post("/approve/{request_id}", response_model=ApprovalResponse)
async def approve_request(
    request: Request,
    request_id: int,
    payload: dict = Depends(verify_token)
):
    """
    Approve a doctor submission (updates status in SQLite)
    
    Requires authentication.
    """
    
    ensure_status_column()
    
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Get the submission
        cursor.execute('SELECT * FROM doctor_outbreaks WHERE id = ?', (request_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check if already processed
        if row['status'] == 'approved':
            conn.close()
            raise HTTPException(status_code=400, detail="Request already approved")
        
        if row['status'] == 'rejected':
            conn.close()
            raise HTTPException(status_code=400, detail="Request was previously rejected")
        
        # Update SQLite status to approved
        cursor.execute(
            'UPDATE doctor_outbreaks SET status = ? WHERE id = ?',
            ('approved', request_id)
        )
        conn.commit()
        conn.close()
        
        # AUDIT LOG
        log_audit_event(
            event="OUTBREAK_APPROVED",
            actor_id=str(payload.get("sub")),
            actor_role="admin",
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"request_id": request_id, "disease": row['disease_type']}
        )
        
        return ApprovalResponse(
            success=True,
            message=f"Request approved! Outbreak data will appear in dashboard.",
            outbreak_id=str(request_id)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving request: {str(e)}")


@router.post("/reject/{request_id}", response_model=ApprovalResponse)
async def reject_request(
    request: Request,
    request_id: int,
    payload: dict = Depends(verify_token)
):
    """
    Reject a doctor submission
    
    Requires authentication.
    """
    
    ensure_status_column()
    
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute('SELECT status, disease_type FROM doctor_outbreaks WHERE id = ?', (request_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Request not found")
        
        if row['status'] == 'approved':
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot reject already approved request")
        
        # Update status
        cursor.execute(
            'UPDATE doctor_outbreaks SET status = ? WHERE id = ?',
            ('rejected', request_id)
        )
        conn.commit()
        conn.close()
        
        # AUDIT LOG
        log_audit_event(
            event="OUTBREAK_REJECTED",
            actor_id=str(payload.get("sub")),
            actor_role="admin",
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"request_id": request_id, "disease": row['disease_type']}
        )
        
        return ApprovalResponse(
            success=True,
            message="Request rejected"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting request: {str(e)}")


@router.get("/all-requests")
async def get_all_requests(payload: dict = Depends(verify_token)):
    """
    Get all doctor submissions with their status
    
    Requires authentication.
    """
    
    ensure_status_column()
    
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM doctor_outbreaks 
            ORDER BY created_at DESC
            LIMIT 100
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        requests = []
        for row in rows:
            requests.append({
                "id": row['id'],
                "disease_type": row['disease_type'],
                "patient_count": row['patient_count'],
                "severity": row['severity'],
                "location_name": row['location_name'],
                "city": row['city'],
                "state": row['state'],
                "date_reported": row['date_reported'],
                "status": row['status'] or 'pending',
                "created_at": row['created_at']
            })
        
        return {
            "requests": requests,
            "total": len(requests)
        }
    
    except Exception as e:
        return {"requests": [], "total": 0, "error": str(e)}
