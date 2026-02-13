from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class AuthEvent(db.Model):
    __tablename__ = 'auth_events'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    email = db.Column(db.String(255))
    
    event_type = db.Column(db.String(50), nullable=False)
    
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text)
    success = db.Column(db.Boolean, nullable=False)
    failure_reason = db.Column(db.Text)
    
    metadata_json = db.Column(JSONB)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
