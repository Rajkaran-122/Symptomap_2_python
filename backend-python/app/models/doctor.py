"""
Doctor Station Models
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class DoctorOutbreak(Base):
    __tablename__ = "doctor_outbreaks"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_type = Column(String(100), nullable=False)
    patient_count = Column(Integer, nullable=False)
    severity = Column(String(50), nullable=False)
    
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    
    description = Column(Text)
    date_reported = Column(DateTime(timezone=True))
    submitted_by = Column(String(100))  # Doctor ID or Name
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default='pending')  # pending, approved, rejected

class DoctorAlert(Base):
    __tablename__ = "doctor_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    
    latitude = Column(Float)
    longitude = Column(Float)
    affected_area = Column(String(255))
    
    expiry_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default='active')
