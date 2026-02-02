"""
Hospital API Endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import defer
from typing import List, Optional

from app.core.database import get_db
from app.models.outbreak import Hospital

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


@router.get("/")
async def list_hospitals(
    state: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db)
):
    """List all hospitals with optional filters"""
    query = select(Hospital).options(defer(Hospital.location))
    
    if state:
        query = query.where(Hospital.state == state)
    if city:
        query = query.where(Hospital.city == city)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    hospitals = result.scalars().all()
    
    return [
        {
            "id": str(h.id),
            "name": h.name,
            "address": h.address,
            "city": h.city,
            "state": h.state,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "total_beds": h.total_beds,
            "icu_beds": h.icu_beds,
            "available_beds": h.available_beds,
            "hospital_type": h.hospital_type
        }
        for h in hospitals
    ]


@router.get("/geojson")
async def get_hospitals_geojson(
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get hospitals as GeoJSON for map visualization"""
    query = select(Hospital).options(defer(Hospital.location))
    
    if state:
        query = query.where(Hospital.state == state)
    
    result = await db.execute(query)
    hospitals = result.scalars().all()
    
    features = []
    for h in hospitals:
        if h.latitude and h.longitude:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [h.longitude, h.latitude]
                },
                "properties": {
                    "id": str(h.id),
                    "name": h.name,
                    "city": h.city,
                    "state": h.state,
                    "total_beds": h.total_beds,
                    "available_beds": h.available_beds,
                    "hospital_type": h.hospital_type
                }
            })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/states")
async def get_states_with_hospitals(
    db: AsyncSession = Depends(get_db)
):
    """Get list of states that have hospitals"""
    from sqlalchemy import distinct, func
    
    query = select(Hospital.state, func.count(Hospital.id).label("count")).group_by(Hospital.state)
    result = await db.execute(query)
    states = result.all()
    
    return {
        "states": [{"name": s[0], "hospital_count": s[1]} for s in states if s[0]],
        "total_states": len([s for s in states if s[0]])
    }
