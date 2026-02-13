"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database (SQLite by default for easy deployment)
    @property
    def DATABASE_URL(self) -> str:
        return "sqlite+aiosqlite:///c:/Users/digital metro/Documents/sympto-pulse-map-main/backend-python/symptomap.db"

    def __init__(self, **values):
        super().__init__(**values)
        print(f"DEBUG: Config resolved DATABASE_URL to: {self.DATABASE_URL}")
    PGSSLMODE: str = "prefer"
    
    # Redis (optional - app uses mock if not provided)
    REDIS_URL: Optional[str] = None
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour for access token
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days for refresh token
    
    # Doctor Password
    DOCTOR_PASSWORD: str = "Doctor@SymptoMap2025"
    
    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    
    # Email Service (Resend - Free Tier: 3K/month)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@symptomap.com"
    EMAIL_FROM_NAME: str = "SymptoMap"
    
    # Legacy SendGrid (optional fallback)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "alerts@symptomap.com"
    SENDGRID_FROM_NAME: str = "SymptoMap"
    
    # Twilio (optional SMS)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - Include all Vercel preview URLs and production domains
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://symptomap-2-python.vercel.app",
        "https://symptomap-2-python-git-main.vercel.app",
        "https://symptomap-2-python-1.onrender.com",
        # Vercel preview URLs pattern (handled in middleware)
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ML Service (optional)
    ML_SERVICE_URL: str = "http://localhost:8001"
    
    # Sentry Error Tracking (Free Tier: 5K errors/month)
    SENTRY_DSN: str = ""
    
    # Security Settings
    BCRYPT_COST_FACTOR: int = 12
    PASSWORD_MIN_LENGTH: int = 12
    ACCOUNT_LOCKOUT_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15

    def model_post_init(self, __context):
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET_KEY == "change-this-secret-key-in-production":
                raise ValueError("FATAL: JWT_SECRET_KEY must be set in production environment!")
            if self.DOCTOR_PASSWORD == "Doctor@SymptoMap2025":
                print("WARNING: Using default DOCTOR_PASSWORD in production!")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()


def get_sqlite_db_path() -> str:
    """Get the SQLite database file path from DATABASE_URL"""
    db_url = settings.DATABASE_URL
    # Remove sqlite:/// prefix and handle both formats
    if db_url.startswith("sqlite:///"):
        path = db_url.replace("sqlite:///", "")
    elif db_url.startswith("sqlite+aiosqlite:///"):
        path = db_url.replace("sqlite+aiosqlite:///", "")
    else:
        # Default fallback
        path = "./symptomap.db"
    
    # Convert relative paths to absolute
    import os
    if not os.path.isabs(path):
        # Get the project root (where the database should be)
        path = os.path.abspath(path)
    
        path = os.path.abspath(path)
    
    print(f"DEBUG: Resolved SQLite DB path: {path}")
    return path

