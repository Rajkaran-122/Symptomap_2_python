"""
Outbreak database models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.types import UUID, JSONB, Geography


class Hospital(Base):
    """Hospital model"""
    
    __tablename__ = "hospitals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    # Location storage - using lat/lng for simplicity
    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)  # Optional for compatibility
    
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    pincode = Column(String(20))
    
    phone = Column(String(20))
    email = Column(String(255))
    
    total_beds = Column(Integer)
    icu_beds = Column(Integer)
    available_beds = Column(Integer)
    
    hospital_type = Column(String(50))  # government, private, charitable
    registration_number = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Outbreak(Base):
    """Outbreak report model"""
    
    __tablename__ = "outbreaks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    disease_type = Column(String(100), nullable=False, index=True)
    patient_count = Column(Integer, nullable=False)
    date_started = Column(DateTime(timezone=True), nullable=False)
    date_reported = Column(DateTime(timezone=True), server_default=func.now())
    
    severity = Column(String(50))  # mild, moderate, severe
    age_distribution = Column(JSONB)  # {"0-18": 10, "19-40": 25, ...}
    gender_distribution = Column(JSONB)  # {"male": 30, "female": 20, ...}
    symptoms = Column(JSONB)  # ["fever", "cough", "body_ache"]
    notes = Column(Text)
    
    # Location storage - using lat/lng for simplicity
    latitude = Column(Float)
    longitude = Column(Float)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)  # Optional for compatibility
    
    verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verification_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Prediction(Base):
    """Prediction model"""
    
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_type = Column(String(50))  # time_series, geographic_spread
    disease_type = Column(String(100), index=True)
    reference_outbreak_id = Column(UUID(as_uuid=True), ForeignKey("outbreaks.id"))
    
    location = Column(Geography(geometry_type='POINT', srid=4326))
    zone_name = Column(String(255))
    
    prediction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_cases = Column(Integer)
    confidence_interval = Column(JSONB)  # {"lower": 45, "upper": 95, "mean": 70}
    
    risk_score = Column(Integer)  # 0-10
    risk_level = Column(String(50))  # safe, low, medium, high, critical
    probability_of_spread = Column(Integer)  # percentage
    estimated_days_to_spread = Column(Integer)
    
    model_version = Column(String(50))
    model_confidence = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # For validation later
    actual_cases = Column(Integer)
    accuracy_score = Column(Integer)


class Alert(Base):
    """Alert model"""
    
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"))
    
    alert_type = Column(String(50), nullable=False)  # outbreak, high_risk, critical
    severity = Column(String(50), nullable=False, index=True)  # info, warning, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    location = Column(Geography(geometry_type='POINT', srid=4326))
    zone_name = Column(String(255))
    
    recipients = Column(JSONB, nullable=False)  # [user_ids]
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    delivery_status = Column(JSONB)  # {"email": "sent", "sms": "delivered"}
    acknowledged_by = Column(JSONB)  # [{"user_id": "...", "timestamp": "..."}]
    
    expires_at = Column(DateTime(timezone=True))
