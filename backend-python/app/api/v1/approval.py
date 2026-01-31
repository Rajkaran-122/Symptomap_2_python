"""
Admin Approval API Endpoints
Allows admins to review, approve, or reject doctor submissions
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.api.v1.auth import get_current_user, get_admin_user
from app.models.user import User
from app.models.doctor import DoctorOutbreak
from app.core.audit import log_audit_event

router = APIRouter(prefix="/admin", tags=["Admin Approval"])


class PendingRequest(BaseModel):
    id: int
    disease_type: str
    patient_count: int
    severity: str
    latitude: Optional[float]
    longitude: Optional[float]
    location_name: Optional[str]
    city: Optional[str]
    state: Optional[str]
    description: Optional[str]
    date_reported: Optional[str]
    submitted_by: Optional[str]
    # created_at type might need handling if it's datetime
    status: str

    class Config:
        from_attributes = True


class ApprovalResponse(BaseModel):
    success: bool
    message: str
    outbreak_id: Optional[str] = None


@router.get("/pending", response_model=List[PendingRequest])
async def get_pending_requests(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pending doctor submissions awaiting approval
    
    Requires admin privileges.
    """
    try:
        result = await db.execute(
            select(DoctorOutbreak)
            .where(DoctorOutbreak.status == 'pending')
            .order_by(desc(DoctorOutbreak.created_at))
        )
        outbreaks = result.scalars().all()
        
        # Convert to Pydantic models - handle partial updates if fields missing
        response_list = []
        for o in outbreaks:
            response_list.append(PendingRequest(
                id=o.id,
                disease_type=o.disease_type,
                patient_count=o.patient_count,
                severity=o.severity,
                latitude=o.latitude,
                longitude=o.longitude,
                location_name=o.location_name,
                city=o.city,
                state=o.state,
                description=o.description,
                date_reported=o.date_reported.isoformat() if o.date_reported else None,
                submitted_by=o.submitted_by,
                status=o.status
            ))
            
        return response_list
    
    except Exception as e:
        import traceback
        print(f"Error fetching pending requests: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching pending requests: {str(e)}")


@router.post("/approve/{request_id}", response_model=ApprovalResponse)
async def approve_request(
    request: Request,
    request_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a doctor submission
    
    Requires admin privileges.
    """
    try:
        # Get the submission
        result = await db.execute(select(DoctorOutbreak).where(DoctorOutbreak.id == request_id))
        outbreak = result.scalar_one_or_none()
        
        if not outbreak:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Check if already processed
        if outbreak.status == 'approved':
            raise HTTPException(status_code=400, detail="Request already approved")
        
        if outbreak.status == 'rejected':
            raise HTTPException(status_code=400, detail="Request was previously rejected")
        
        # Update status
        outbreak.status = 'approved'
        await db.commit()
        await db.refresh(outbreak)
        
        # AUDIT LOG
        log_audit_event(
            event="OUTBREAK_APPROVED",
            actor_id=str(current_user.id),
            actor_role="admin",
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"request_id": request_id, "disease": outbreak.disease_type}
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
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a doctor submission
    
    Requires admin privileges.
    """
    try:
        # Get the submission
        result = await db.execute(select(DoctorOutbreak).where(DoctorOutbreak.id == request_id))
        outbreak = result.scalar_one_or_none()
        
        if not outbreak:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if outbreak.status == 'approved':
            raise HTTPException(status_code=400, detail="Cannot reject already approved request")
        
        # Update status
        outbreak.status = 'rejected'
        await db.commit()
        await db.refresh(outbreak)
        
        # AUDIT LOG
        log_audit_event(
            event="OUTBREAK_REJECTED",
            actor_id=str(current_user.id),
            actor_role="admin",
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"request_id": request_id, "disease": outbreak.disease_type}
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
async def get_all_requests(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all doctor submissions with their status
    
    Requires admin privileges.
    """
    try:
        result = await db.execute(
            select(DoctorOutbreak)
            .order_by(desc(DoctorOutbreak.created_at))
            .limit(100)
        )
        outbreaks = result.scalars().all()
        
        requests = []
        for row in outbreaks:
            requests.append({
                "id": row.id,
                "disease_type": row.disease_type,
                "patient_count": row.patient_count,
                "severity": row.severity,
                "location_name": row.location_name,
                "city": row.city,
                "state": row.state,
                "date_reported": row.date_reported.isoformat() if row.date_reported else None,
                "status": row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "requests": requests,
            "total": len(requests)
        }
    
    except Exception as e:
        return {"requests": [], "total": 0, "error": str(e)}
