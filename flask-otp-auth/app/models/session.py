from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    refresh_token_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    access_token_jti = db.Column(db.String(255), nullable=False)
    
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text)
    device_fingerprint = db.Column(db.String(255))
    
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
