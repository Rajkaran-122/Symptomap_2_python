"""
User notification preferences model
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, ARRAY, Time
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.types import UUID


class NotificationPreference(Base):
    """User notification preferences"""
    
    __tablename__ = "user_notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Subscription preferences
    region_subscriptions = Column(JSON, default=[])  # List of regions to subscribe
    disease_subscriptions = Column(JSON, default=[])  # List of diseases to subscribe
    
    # Notification settings
    min_severity = Column(String(20), default="info")  # info, warning, critical, emergency
    frequency = Column(String(20), default="real_time")  # real_time, daily, weekly
    
    # Channel preferences
    channels = Column(JSON, default={
        "in_app": True,
        "email": False,
        "sms": False,
        "push": False
    })
    
    # Quiet hours (don't disturb during these times, except emergencies)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))    # HH:MM format
    
    # Status
    enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "region_subscriptions": self.region_subscriptions or [],
            "disease_subscriptions": self.disease_subscriptions or [],
            "min_severity": self.min_severity,
            "frequency": self.frequency,
            "channels": self.channels or {"in_app": True},
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
