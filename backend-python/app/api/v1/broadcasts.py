"""
Broadcast Management Endpoints
Admin creates, users view health broadcasts
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from app.core.database import get_db
from app.models.broadcast import Broadcast
from app.models.user import User
from app.api.v1.auth import get_current_user, get_admin_user, get_current_user_optional

router = APIRouter(prefix="/broadcasts", tags=["Broadcasts"])


# =============================================================================
# PERMISSION HELPERS
# =============================================================================

async def get_user_or_above(
    current_user: User = Depends(get_current_user)
) -> User:
    """Allow user, patient, doctor, or admin roles"""
    allowed_roles = ["user", "patient", "doctor", "admin", "public_health_official"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Insufficient permissions."
        )
    return current_user


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class BroadcastCreate(BaseModel):
    """Create new broadcast"""
    title: str = Field(..., max_length=200)
    content: str = Field(..., min_length=10)
    severity: str = Field(default="info", pattern=r'^(info|warning|critical|emergency)$')
    region: Optional[str] = Field(None, description="Target region (null = all)")
    channels: List[str] = Field(default=["in_app"])
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class BroadcastUpdate(BaseModel):
    """Update broadcast"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    severity: Optional[str] = Field(None, pattern=r'^(info|warning|critical|emergency)$')
    region: Optional[str] = None
    channels: Optional[List[str]] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class BroadcastResponse(BaseModel):
    """Broadcast response"""
    id: str
    title: str
    content: str
    severity: str
    region: Optional[str]
    channels: List[str]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    scheduled_for: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    is_automated: bool

    class Config:
        from_attributes = True


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("", response_model=List[BroadcastResponse])
async def list_broadcasts(
    region: Optional[str] = Query(None, description="Filter by region"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    active_only: bool = Query(True, description="Show only active broadcasts"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List broadcasts (accessible to all users, even guests)
    
    - Users see broadcasts for their region + global broadcasts
    - Admins see all broadcasts
    """
    
    # Build query
    conditions = []
    
    if active_only:
        conditions.append(Broadcast.is_active == True)
        # Filter out expired broadcasts
        conditions.append(
            or_(
                Broadcast.expires_at == None,
                Broadcast.expires_at > datetime.now(timezone.utc)
            )
        )
    
    # Region filtering
    if region:
        conditions.append(
            or_(
                Broadcast.region == region,
                Broadcast.region == None
            )
        )
    elif current_user and current_user.role not in ["admin", "public_health_official"]:
        # Non-admin users only see their region + global broadcasts
        if current_user.region:
            conditions.append(
                or_(
                    Broadcast.region == current_user.region,
                    Broadcast.region == None
                )
            )
    
    if severity:
        conditions.append(Broadcast.severity == severity)
    
    # Execute query
    query = select(Broadcast)
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Broadcast.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    broadcasts = result.scalars().all()
    
    return [
        BroadcastResponse(
            id=str(b.id),
            title=b.title,
            content=b.content,
            severity=b.severity,
            region=b.region,
            channels=b.channels or ["in_app"],
            created_by=str(b.created_by) if b.created_by else None,
            created_at=b.created_at,
            updated_at=b.updated_at,
            scheduled_for=b.scheduled_for,
            expires_at=b.expires_at,
            is_active=b.is_active,
            is_automated=b.is_automated or False
        )
        for b in broadcasts
    ]


@router.get("/{broadcast_id}", response_model=BroadcastResponse)
async def get_broadcast(
    broadcast_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_user_or_above)
):
    """Get single broadcast by ID"""
    
    try:
        bid = uuid.UUID(broadcast_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid broadcast ID format")
    
    result = await db.execute(select(Broadcast).where(Broadcast.id == bid))
    broadcast = result.scalar_one_or_none()
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Check access for non-admin users
    if current_user.role not in ["admin", "public_health_official"]:
        if broadcast.region and broadcast.region != current_user.region:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this broadcast"
            )
    
    return BroadcastResponse(
        id=str(broadcast.id),
        title=broadcast.title,
        content=broadcast.content,
        severity=broadcast.severity,
        region=broadcast.region,
        channels=broadcast.channels or ["in_app"],
        created_by=str(broadcast.created_by) if broadcast.created_by else None,
        created_at=broadcast.created_at,
        updated_at=broadcast.updated_at,
        scheduled_for=broadcast.scheduled_for,
        expires_at=broadcast.expires_at,
        is_active=broadcast.is_active,
        is_automated=broadcast.is_automated or False
    )


@router.post("/", response_model=BroadcastResponse, status_code=status.HTTP_201_CREATED)
async def create_broadcast(
    broadcast_data: BroadcastCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Create new broadcast (Admin only)
    
    - Immediately active unless scheduled_for is set
    - Set expires_at for time-limited announcements
    """
    
    new_broadcast = Broadcast(
        id=uuid.uuid4(),
        title=broadcast_data.title,
        content=broadcast_data.content,
        severity=broadcast_data.severity,
        region=broadcast_data.region,
        channels=broadcast_data.channels,
        scheduled_for=broadcast_data.scheduled_for,
        expires_at=broadcast_data.expires_at,
        created_by=admin.id,
        is_active=True,
        is_automated=False
    )
    
    db.add(new_broadcast)
    await db.commit()
    await db.refresh(new_broadcast)
    
    return BroadcastResponse(
        id=str(new_broadcast.id),
        title=new_broadcast.title,
        content=new_broadcast.content,
        severity=new_broadcast.severity,
        region=new_broadcast.region,
        channels=new_broadcast.channels or ["in_app"],
        created_by=str(new_broadcast.created_by) if new_broadcast.created_by else None,
        created_at=new_broadcast.created_at,
        updated_at=new_broadcast.updated_at,
        scheduled_for=new_broadcast.scheduled_for,
        expires_at=new_broadcast.expires_at,
        is_active=new_broadcast.is_active,
        is_automated=new_broadcast.is_automated
    )


@router.put("/{broadcast_id}", response_model=BroadcastResponse)
async def update_broadcast(
    broadcast_id: str,
    updates: BroadcastUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Update broadcast (Admin only)"""
    
    try:
        bid = uuid.UUID(broadcast_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid broadcast ID format")
    
    result = await db.execute(select(Broadcast).where(Broadcast.id == bid))
    broadcast = result.scalar_one_or_none()
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Update fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(broadcast, field, value)
    
    await db.commit()
    await db.refresh(broadcast)
    
    return BroadcastResponse(
        id=str(broadcast.id),
        title=broadcast.title,
        content=broadcast.content,
        severity=broadcast.severity,
        region=broadcast.region,
        channels=broadcast.channels or ["in_app"],
        created_by=str(broadcast.created_by) if broadcast.created_by else None,
        created_at=broadcast.created_at,
        updated_at=broadcast.updated_at,
        scheduled_for=broadcast.scheduled_for,
        expires_at=broadcast.expires_at,
        is_active=broadcast.is_active,
        is_automated=broadcast.is_automated or False
    )


@router.delete("/{broadcast_id}")
async def delete_broadcast(
    broadcast_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    Soft delete broadcast (Admin only)
    
    Sets is_active to False instead of deleting from database.
    """
    
    try:
        bid = uuid.UUID(broadcast_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid broadcast ID format")
    
    result = await db.execute(select(Broadcast).where(Broadcast.id == bid))
    broadcast = result.scalar_one_or_none()
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    broadcast.is_active = False
    await db.commit()
    
    return {
        "message": "Broadcast archived successfully",
        "broadcast_id": broadcast_id
    }


@router.get("/stats/summary")
async def get_broadcast_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Get broadcast statistics (Admin only)"""
    
    # Total broadcasts
    total_result = await db.execute(select(Broadcast))
    total = len(total_result.scalars().all())
    
    # Active broadcasts
    active_result = await db.execute(
        select(Broadcast).where(
            and_(
                Broadcast.is_active == True,
                or_(
                    Broadcast.expires_at == None,
                    Broadcast.expires_at > datetime.now(timezone.utc)
                )
            )
        )
    )
    active = len(active_result.scalars().all())
    
    return {
        "total_broadcasts": total,
        "active_broadcasts": active,
        "archived_broadcasts": total - active
    }
