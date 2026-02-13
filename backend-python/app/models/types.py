
"""
Cross-database compatible types
"""
import uuid
from sqlalchemy import JSON, String, Uuid as SQLAlchemyUuid
from sqlalchemy.types import TypeDecorator

# Use generic JSON
JSONB = JSON

# Use generic UUID
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type for PostgreSQL,
    String(36) for others to ensure dash consistency in SQLite.
    """
    impl = String
    cache_ok = True

    def __init__(self, as_uuid=True):
        self.as_uuid = as_uuid
        super().__init__()

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value).lower()

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            import uuid as python_uuid
            try:
                return python_uuid.UUID(value)
            except (ValueError, AttributeError):
                return value
        return value

# Mock Geography as String for SQLite compatibility
class Geography(TypeDecorator):
    """
    Geography type that falls back to String for SQLite/Lite mode.
    Note: Real spatial queries will fail if not handled in service layer.
    """
    impl = String
    cache_ok = True
    
    def __init__(self, geometry_type='POINT', srid=4326, **kwargs):
        super().__init__(**kwargs)
