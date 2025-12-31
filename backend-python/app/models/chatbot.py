"""
Chatbot conversation database models
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.types import UUID, JSONB, Geography


class ChatbotConversation(Base):
    """Chatbot conversation model"""
    
    __tablename__ = "chatbot_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for anonymous
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    
    # Location
    location = Column(Geography(geometry_type='POINT', srid=4326))
    city = Column(String(100))
    country = Column(String(100))
    
    # Conversation state
    conversation_state = Column(String(50), default="greeting")
    conversation_data = Column(JSONB, default=[])  # Full message history
    user_info = Column(JSONB, default={})  # Age, gender, etc.
    
    # Medical assessment
    soap_note = Column(JSONB)
    severity_assessment = Column(String(50))  # emergency, urgent, routine
    primary_symptoms = Column(JSONB, default=[])
    suspected_conditions = Column(JSONB, default=[])
    recommendations = Column(Text)
    
    # Feedback
    user_feedback = Column(Integer)  # 1-5 rating
    feedback_comments = Column(Text)
    
    # Quality control
    flagged_for_review = Column(String(50), default="false")
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AnonymousSymptomReport(Base):
    """Anonymous symptom reports for surveillance"""
    
    __tablename__ = "anonymous_symptom_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chatbot_conversations.id"))
    
    report_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326))
    city = Column(String(100))
    district = Column(String(100))
    
    # Demographics (anonymized)
    age_group = Column(String(20))  # 0-18, 19-40, 41-60, 60+
    gender = Column(String(20))  # male, female, other
    
    # Symptoms
    symptoms = Column(JSONB)
    suspected_disease = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiseaseInfo(Base):
    """Disease information database"""
    
    __tablename__ = "disease_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disease_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))  # viral, bacterial, parasitic, fungal
    
    typical_incubation_period_days = Column(Integer)
    typical_duration_days = Column(Integer)
    
    transmission_modes = Column(JSONB)  # ["airborne", "contact", "vector"]
    common_symptoms = Column(JSONB)
    red_flag_symptoms = Column(JSONB)
    prevention_measures = Column(JSONB)
    treatment_options = Column(JSONB)
    
    seasonal_pattern = Column(String(100))
    r0_value = Column(Integer)  # Basic reproduction number
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
