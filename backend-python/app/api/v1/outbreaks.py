"""
Outbreak management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.models.outbreak import Outbreak, Hospital
from app.models.user import User
from app.api.v1.auth import get_current_user


router = APIRouter(prefix="/outbreaks", tags=["Outbreaks"])


# Request/Response models
class OutbreakCreate(BaseModel):
    disease_type: str
    patient_count: int
    date_started: datetime
    severity: str  # mild, moderate, severe
    age_distribution: Optional[dict] = None
    gender_distribution: Optional[dict] = None
    symptoms: Optional[List[str]] = None
    notes: Optional[str] = None
    
    # Manual entry fields (for admins/doctors reporting for others)
    hospital_name: Optional[str] = None
    location: Optional[dict] = None  # {"lat": 19.xxx, "lng": 72.xxx}


class OutbreakResponse(BaseModel):
    id: str
    hospital: dict
    disease_type: str
    patient_count: int
    date_started: datetime
    severity: str
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=dict)
async def create_outbreak(
    outbreak_data: OutbreakCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new outbreak report (public endpoint for testing)"""
    
    hospital = None
    
    try:
        # CASE 1: Manual Entry (Admin/PHO providing hospital details directly)
        if outbreak_data.hospital_name and outbreak_data.location:
            # Check if hospital exists by name (simple check)
            result = await db.execute(
                select(Hospital).where(Hospital.name == outbreak_data.hospital_name)
            )
            hospital = result.scalar_one_or_none()
            
            # Support both lat/lng and latitude/longitude keys
            lat_val = outbreak_data.location.get("lat") or outbreak_data.location.get("latitude") or 0
            lng_val = outbreak_data.location.get("lng") or outbreak_data.location.get("longitude") or 0
            lat = float(lat_val)
            lng = float(lng_val)
            city = outbreak_data.location.get("city", "Unknown")
            state = outbreak_data.location.get("state", "Unknown")
            
            if not hospital:
                # Create new hospital on the fly - use lat/lng columns directly
                hospital = Hospital(
                    name=outbreak_data.hospital_name,
                    address="Manual Entry",
                    latitude=lat,
                    longitude=lng,
                    location=f"POINT({lng} {lat})",  # Store as WKT string
                    city=city,
                    state=state,
                    hospital_type="Manual Entry"
                )
                db.add(hospital)
                await db.commit()
                await db.refresh(hospital)
        
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital not found. Please provide hospital_name and location for manual entry."
            )
        
        # Get location for outbreak
        lat_val = 0
        lng_val = 0
        
        if outbreak_data.location:
             lat_val = outbreak_data.location.get("lat") or outbreak_data.location.get("latitude") or 0
             lng_val = outbreak_data.location.get("lng") or outbreak_data.location.get("longitude") or 0
        else:
             lat_val = hospital.latitude or 0
             lng_val = hospital.longitude or 0
             
        lat = float(lat_val)
        lng = float(lng_val)
        
        # Create outbreak
        outbreak = Outbreak(
            hospital_id=hospital.id,
            reported_by=None,  # Allow null for testing
            disease_type=outbreak_data.disease_type,
            patient_count=outbreak_data.patient_count,
            date_started=outbreak_data.date_started,
            severity=outbreak_data.severity,
            age_distribution=outbreak_data.age_distribution,
            gender_distribution=outbreak_data.gender_distribution,
            symptoms=outbreak_data.symptoms,
            notes=outbreak_data.notes,
            latitude=lat,
            longitude=lng,
            location=f"POINT({lng} {lat})",  # Store as WKT string
            verified=True  # Auto-verify for testing
        )
        
        db.add(outbreak)
        await db.commit()
        await db.refresh(outbreak)
        
        return {
            "id": str(outbreak.id),
            "hospital_name": hospital.name,
            "disease_type": outbreak.disease_type,
            "patient_count": outbreak.patient_count,
            "severity": outbreak.severity,
            "message": "Outbreak reported successfully."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating outbreak: {str(e)}"
        )


@router.get("/", response_model=List[dict])
async def list_outbreaks_array(
    disease_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    severity: Optional[str] = None,
    verified: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List outbreaks with filters - returns raw array"""
    result = await _get_outbreaks(db, disease_type, start_date, end_date, severity, verified, None, limit, offset)
    return result


@router.get("/all")
async def list_outbreaks_wrapped(
    disease_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    severity: Optional[str] = None,
    verified: Optional[bool] = None,
    days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List outbreaks with filters - returns wrapped response for Admin Dashboard"""
    result = await _get_outbreaks(db, disease_type, start_date, end_date, severity, verified, days, limit, offset)
    return {
        "outbreaks": result,
        "count": len(result)
    }


async def _get_outbreaks(
    db: AsyncSession,
    disease_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    severity: Optional[str] = None,
    verified: Optional[bool] = None,
    days: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
):
    """Internal helper to get outbreaks with filters"""
    from sqlalchemy.orm import defer
    from datetime import timedelta, timezone
    
    # Build query - defer loading the location Geography field to avoid deserialization errors
    query = select(Outbreak, Hospital).join(
        Hospital, Outbreak.hospital_id == Hospital.id
    ).options(
        defer(Outbreak.location),  # Don't load location field
        defer(Hospital.location)   # Don't load location field
    )
    
    # Apply filters
    filters = []
    if disease_type:
        filters.append(Outbreak.disease_type == disease_type)
    if start_date:
        filters.append(Outbreak.date_reported >= start_date)
    if end_date:
        filters.append(Outbreak.date_reported <= end_date)
    if severity:
        filters.append(Outbreak.severity == severity)
    if verified is not None:
        filters.append(Outbreak.verified == verified)
    if days:
        # Use naive datetime for SQLite comparison if needed
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        # For SQLite, sometimes naive comparison works better with func.now() defaults
        if "sqlite" in str(db.bind.url):
             cutoff = cutoff.replace(tzinfo=None)
        filters.append(Outbreak.date_reported >= cutoff)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Outbreak.date_reported.desc())
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    rows = result.all()
    
    outbreaks = []
    for outbreak, hospital in rows:
        # Use latitude/longitude from database instead of location Geography
        outbreak_dict = {
            "id": str(outbreak.id),
            "hospital": {
                "id": str(hospital.id),
                "name": hospital.name,
                "location": {
                    "lat": hospital.latitude if hospital.latitude else 0,
                    "lng": hospital.longitude if hospital.longitude else 0,
                    "latitude": hospital.latitude if hospital.latitude else 0,
                    "longitude": hospital.longitude if hospital.longitude else 0,
                    "city": hospital.city,
                    "state": hospital.state
                }
            },
            "city": hospital.city,  # Direct access for map
            "state": hospital.state,  # Direct access for map
            "disease": outbreak.disease_type,  # Alias for AdminDashboard
            "disease_type": outbreak.disease_type,
            "cases": outbreak.patient_count,  # Alias for AdminDashboard
            "patient_count": outbreak.patient_count,
            "date_started": outbreak.date_started.isoformat(),
            "reported_date": outbreak.date_reported.isoformat() if outbreak.date_reported else None,  # Alias
            "date_reported": outbreak.date_reported.isoformat() if outbreak.date_reported else None,
            "severity": outbreak.severity,
            "age_distribution": outbreak.age_distribution,
            "gender_distribution": outbreak.gender_distribution,
            "symptoms": outbreak.symptoms,
            "notes": outbreak.notes,
            "verified": outbreak.verified,
            "location": {
                "name": hospital.name,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude
            },
            "created_at": outbreak.created_at.isoformat() if outbreak.created_at else None,
            "updated_at": outbreak.updated_at.isoformat() if outbreak.updated_at else None
        }
        outbreaks.append(outbreak_dict)
    
    return outbreaks


@router.get("/pending-count")
async def get_pending_outbreak_count(
    db: AsyncSession = Depends(get_db)
):
    """Get count of pending outbreaks"""
    from app.models.doctor import DoctorOutbreak
    result = await db.execute(
        select(func.count()).select_from(DoctorOutbreak).where(DoctorOutbreak.status == 'pending')
    )
    count = result.scalar_one()
    return {"count": count}


@router.get("/stats")
async def get_outbreak_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated outbreak statistics for Admin Dashboard"""
    
    # 1. Total Reports
    total_query = select(func.count(Outbreak.id))
    total_result = await db.execute(total_query)
    total_reports = total_result.scalar() or 0
    
    # 2. Pending Review (Not Verified)
    pending_query = select(func.count(Outbreak.id)).where(Outbreak.verified == False)
    pending_result = await db.execute(pending_query)
    pending_review = pending_result.scalar() or 0
    
    # 3. High Priority (Severe)
    severe_query = select(func.count(Outbreak.id)).where(Outbreak.severity == 'severe')
    severe_result = await db.execute(severe_query)
    high_priority = severe_result.scalar() or 0
    
    # 4. Active Cases (Sum of patients)
    cases_query = select(func.sum(Outbreak.patient_count))
    cases_result = await db.execute(cases_query)
    active_cases = cases_result.scalar() or 0
    
    return {
        "total_reports": total_reports,
        "pending_review": pending_review,
        "high_priority": high_priority,
        "active_cases": active_cases
    }


@router.get("/{outbreak_id}")
async def get_outbreak(
    outbreak_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed outbreak information"""
    
    result = await db.execute(
        select(Outbreak, Hospital).join(
            Hospital, Outbreak.hospital_id == Hospital.id
        ).where(Outbreak.id == outbreak_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outbreak not found"
        )
    
    outbreak, hospital = row
    
    return {
        "id": str(outbreak.id),
        "hospital": {
            "id": str(hospital.id),
            "name": hospital.name,
            "address": hospital.address,
            "location": {
                "lat": hospital.latitude if hospital.latitude else 0,
                "lng": hospital.longitude if hospital.longitude else 0
            },
            "phone": hospital.phone,
            "total_beds": hospital.total_beds,
            "available_beds": hospital.available_beds
        },
        "disease_type": outbreak.disease_type,
        "patient_count": outbreak.patient_count,
        "date_started": outbreak.date_started,
        "date_reported": outbreak.date_reported,
        "severity": outbreak.severity,
        "age_distribution": outbreak.age_distribution,
        "gender_distribution": outbreak.gender_distribution,
        "symptoms": outbreak.symptoms,
        "notes": outbreak.notes,
        "verified": outbreak.verified
    }


@router.post("/{outbreak_id}/verify")
async def verify_outbreak(
    outbreak_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify outbreak (admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify outbreaks"
        )
    
    result = await db.execute(
        select(Outbreak).where(Outbreak.id == outbreak_id)
    )
    outbreak = result.scalar_one_or_none()
    
    if not outbreak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outbreak not found"
        )
    
    outbreak.verified = True
    outbreak.verified_by = current_user.id
    outbreak.verification_date = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {
        "message": "Outbreak verified successfully",
        "outbreak_id": str(outbreak.id),
        "verified_by": current_user.full_name
    }


@router.post("/{outbreak_id}/verify-public")
async def verify_outbreak_public(
    outbreak_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify outbreak - public endpoint for dashboard (no auth required)"""
    import uuid
    
    try:
        bid = uuid.UUID(outbreak_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid outbreak ID format")
    
    result = await db.execute(
        select(Outbreak).where(Outbreak.id == bid)
    )
    outbreak = result.scalar_one_or_none()
    
    if not outbreak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outbreak not found"
        )
    
    outbreak.verified = True
    outbreak.verification_date = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {
        "message": "Outbreak verified successfully",
        "outbreak_id": str(outbreak.id),
        "verified": True
    }


@router.get("/map/geojson")
async def get_outbreaks_geojson(
    disease_type: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get outbreaks as GeoJSON for map visualization"""
    
    # Get outbreaks from last N days
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    query = select(Outbreak, Hospital).join(
        Hospital, Outbreak.hospital_id == Hospital.id
    ).where(Outbreak.date_reported >= start_date)
    
    if disease_type:
        query = query.where(Outbreak.disease_type == disease_type)
    
    result = await db.execute(query)
    rows = result.all()
    
    features = []
    for outbreak, hospital in rows:
        lng = hospital.longitude if hospital.longitude else 0
        lat = hospital.latitude if hospital.latitude else 0
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "outbreak_id": str(outbreak.id),
                "hospital_name": hospital.name,
                "disease_type": outbreak.disease_type,
                "patient_count": outbreak.patient_count,
                "severity": outbreak.severity,
                "date_reported": outbreak.date_reported.isoformat(),
                "color": _get_severity_color(outbreak.severity)
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def _get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        "severe": "#DC2626",  # red
        "moderate": "#F59E0B",  # amber
        "mild": "#10B981"  # green
    }
    return colors.get(severity, "#6B7280")
