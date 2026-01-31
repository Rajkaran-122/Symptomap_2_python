"""
Outbreak management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
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
            
            lat = float(outbreak_data.location.get("lat", 0))
            lng = float(outbreak_data.location.get("lng", 0))
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
        lat = outbreak_data.location.get("lat", 0) if outbreak_data.location else (hospital.latitude or 0)
        lng = outbreak_data.location.get("lng", 0) if outbreak_data.location else (hospital.longitude or 0)
        
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
@router.get("/all", response_model=List[dict])
async def list_outbreaks(
    disease_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    severity: Optional[str] = None,
    verified: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List outbreaks with filters - using lat/lng instead of Geography"""
    from sqlalchemy.orm import defer
    
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
                    "lng": hospital.longitude if hospital.longitude else 0
                }
            },
            "disease_type": outbreak.disease_type,
            "patient_count": outbreak.patient_count,
            "date_started": outbreak.date_started.isoformat(),
            "date_reported": outbreak.date_reported.isoformat() if outbreak.date_reported else None,
            "severity": outbreak.severity,
            "age_distribution": outbreak.age_distribution,
            "gender_distribution": outbreak.gender_distribution,
            "symptoms": outbreak.symptoms,
            "notes": outbreak.notes,
            "verified": outbreak.verified,
            "created_at": outbreak.created_at.isoformat() if outbreak.created_at else None,
            "updated_at": outbreak.updated_at.isoformat() if outbreak.updated_at else None
        }
        outbreaks.append(outbreak_dict)
    
    return outbreaks


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
