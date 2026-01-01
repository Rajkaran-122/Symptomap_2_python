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
from geoalchemy2.elements import WKTElement
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
    import os
    # Use same path as doctor_station.py
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'symptomap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_status_column():
    """Ensure status column exists in doctor_outbreaks table"""
    conn = get_sqlite_connection()
    cursor = conn.cursor()
    
    # Check if status column exists
    cursor.execute("PRAGMA table_info(doctor_outbreaks)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'status' not in columns:
        cursor.execute("ALTER TABLE doctor_outbreaks ADD COLUMN status TEXT DEFAULT 'pending'")
        conn.commit()
    
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
    request_id: int,
    payload: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a doctor submission and migrate to official PostgreSQL database
    
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
        
        # Create hospital in PostgreSQL if not exists
        lat = float(row['latitude'])
        lng = float(row['longitude'])
        
        try:
            location_geom = WKTElement(f"POINT({lng} {lat})", srid=4326)
        except Exception:
            location_geom = None
        
        # Check if hospital exists
        from sqlalchemy import select
        hospital_result = await db.execute(
            select(Hospital).where(Hospital.name == row['location_name'])
        )
        hospital = hospital_result.scalar_one_or_none()
        
        if not hospital:
            hospital = Hospital(
                name=row['location_name'] or f"Hospital_{request_id}",
                address=f"{row['city']}, {row['state']}",
                latitude=lat,
                longitude=lng,
                location=location_geom,
                city=row['city'],
                state=row['state'],
                hospital_type="Doctor Submission"
            )
            db.add(hospital)
            await db.commit()
            await db.refresh(hospital)
        
        # Create outbreak in PostgreSQL
        outbreak = Outbreak(
            hospital_id=hospital.id,
            reported_by=None,
            disease_type=row['disease_type'],
            patient_count=row['patient_count'],
            date_started=datetime.fromisoformat(row['date_reported'].replace('Z', '+00:00')) if row['date_reported'] else datetime.now(timezone.utc),
            severity=row['severity'],
            notes=row['description'],
            latitude=lat,
            longitude=lng,
            location=location_geom,
            verified=True
        )
        
        db.add(outbreak)
        await db.commit()
        await db.refresh(outbreak)
        
        # Update SQLite status
        cursor.execute(
            'UPDATE doctor_outbreaks SET status = ? WHERE id = ?',
            ('approved', request_id)
        )
        conn.commit()
        conn.close()
        
        return ApprovalResponse(
            success=True,
            message=f"Request approved and added to official database",
            outbreak_id=str(outbreak.id)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving request: {str(e)}")


@router.post("/reject/{request_id}", response_model=ApprovalResponse)
async def reject_request(
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
        cursor.execute('SELECT status FROM doctor_outbreaks WHERE id = ?', (request_id,))
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
