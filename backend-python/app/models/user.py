"""
User database model with MFA support
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.types import UUID


class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(50), nullable=False)  # doctor, admin, public_health_official, patient
    
    # Doctor specific fields
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    medical_license_number = Column(String(100))
    verification_status = Column(String(50), default="pending")  # pending, verified, rejected
    
    # MFA / Two-Factor Authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100))  # TOTP secret
    mfa_backup_codes = Column(JSON)  # Hashed backup codes array
    
    # Security tracking
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(100))
    email_verification_expires = Column(DateTime(timezone=True))
    
    # Password reset
    password_reset_token = Column(String(100))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True)

