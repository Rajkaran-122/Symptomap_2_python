"""
Doctor Station Authentication
Simple password-based authentication for healthcare professionals
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from typing import Optional

router = APIRouter(prefix="/doctor", tags=["Doctor Auth"])

# Security
security = HTTPBearer()

# Configuration from environment variables (BRD compliant)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "symptomap-doctor-secret-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Doctor password from environment (BRD: default "Doctor@SymptoMap2025")
DOCTOR_PASSWORD = os.getenv("DOCTOR_PASSWORD", "Doctor@SymptoMap2025")


class LoginRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
async def doctor_login(request: LoginRequest):
    """
    Doctor login endpoint
    
    Authenticate with password and receive JWT token
    Default password: Doctor@SymptoMap2025
    """
    
    # Verify password
    if request.password != DOCTOR_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
    
    # Create access token
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": "doctor", "role": "doctor"},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )


@router.get("/verify")
async def verify_doctor_token(payload: dict = Depends(verify_token)):
    """
    Verify doctor token is valid
    
    Returns doctor info if token is valid
    """
    return {
        "valid": True,
        "role": payload.get("role"),
        "user": payload.get("sub")
    }
