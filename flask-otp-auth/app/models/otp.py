from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class OTP(db.Model):
    __tablename__ = 'otp_codes'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    otp_hash = db.Column(db.String(255), nullable=False)
    purpose = db.Column(db.String(50), nullable=False) # login, signup, password_reset
    
    sent_via_email = db.Column(db.Boolean, default=False)
    sent_via_sms = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    sms_sent_at = db.Column(db.DateTime)
    
    verification_attempts = db.Column(db.Integer, default=0)
    verified_at = db.Column(db.DateTime)
    
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    is_used = db.Column(db.Boolean, default=False)
    
    ip_address = db.Column(db.String(45)) # IPv6 support
    user_agent = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
