from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class RateLimit(db.Model):
    __tablename__ = 'rate_limits'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    identifier = db.Column(db.String(255), nullable=False)
    identifier_type = db.Column(db.String(20), nullable=False) # email, ip, phone
    action = db.Column(db.String(50), nullable=False)
    
    attempt_count = db.Column(db.Integer, default=1)
    window_start = db.Column(db.DateTime, default=datetime.utcnow)
    blocked_until = db.Column(db.DateTime)
    
    __table_args__ = (
        db.UniqueConstraint('identifier', 'identifier_type', 'action', name='unique_rate_limit'),
    )
