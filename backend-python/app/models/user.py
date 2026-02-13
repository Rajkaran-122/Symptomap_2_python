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
    email = Column(String(255), unique=True, nullable=True, index=True)  # Nullable for OTP users
    password_hash = Column(String(255), nullable=True)  # Nullable for OTP users
    full_name = Column(String(255), nullable=True)  # Can be set later for OTP users
    phone = Column(String(20), unique=True, index=True)  # Unique phone for OTP
    role = Column(String(50), nullable=False)  # doctor, admin, patient, user
    
    # Phone verification for OTP users
    phone_verified = Column(Boolean, default=False)
    region = Column(String(100))  # User's region for targeted broadcasts
    
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
    is_verified = Column(Boolean, default=False)  # OTP email/phone verification complete

    def to_dict(self):
        """Serialize user for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "phone": self.phone,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "region": self.region,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

