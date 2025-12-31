
"""
Cross-database compatible types
"""
from sqlalchemy import JSON, String, Uuid as SQLAlchemyUuid
from sqlalchemy.types import TypeDecorator

# Use generic JSON
JSONB = JSON

# Use generic UUID
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type for PostgreSQL,
    CHAR(32) for others.
    """
    impl = SQLAlchemyUuid
    cache_ok = True

    def __init__(self, as_uuid=True):
        self.as_uuid = as_uuid
        super().__init__()

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
