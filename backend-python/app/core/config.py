"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database (SQLite by default for easy deployment)
    DATABASE_URL: str = "sqlite:///./symptomap.db"
    PGSSLMODE: str = "prefer"
    
    # Redis (optional - app uses mock if not provided)
    REDIS_URL: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Doctor Password
    DOCTOR_PASSWORD: str = "Doctor@SymptoMap2025"
    
    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    
    # SendGrid (optional)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "alerts@symptomap.com"
    SENDGRID_FROM_NAME: str = "SymptoMap"
    
    # Twilio (optional)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # ML Service (optional)
    ML_SERVICE_URL: str = "http://localhost:8001"
    
    # Sentry (optional)
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

