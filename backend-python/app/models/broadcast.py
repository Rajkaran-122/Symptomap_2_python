"""
Broadcast model for health announcements and alerts
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.types import UUID


class Broadcast(Base):
    """Broadcast model for admin health announcements"""
    
    __tablename__ = "broadcasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Severity: info, warning, critical, emergency
    severity = Column(String(20), default="info", nullable=False)
    
    # Targeting
    region = Column(String(100))  # NULL = all regions
    target_audience = Column(JSON, default={"type": "all"})
    
    # Delivery channels: ["in_app", "email", "sms", "push"]
    channels = Column(JSON, default=["in_app"])
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True))  # NULL = immediate
    expires_at = Column(DateTime(timezone=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_automated = Column(Boolean, default=False)  # True if AI-generated
    
    # Additional metadata (AI prediction details, sources, etc.)
    additional_data = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "severity": self.severity,
            "region": self.region,
            "target_audience": self.target_audience,
            "channels": self.channels,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_automated": self.is_automated,
            "metadata": self.additional_data
        }

print("✅ Loaded Broadcast model (renamed schema)")

