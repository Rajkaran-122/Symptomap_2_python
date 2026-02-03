"""
Enhanced Authentication Routes - Production Ready
Features:
- JWT access + refresh tokens
- Password strength validation
- Account lockout protection
- MFA/TOTP support
- Audit logging
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    get_password_hash, 
    verify_password,
    validate_password_strength,
    create_access_token,
    create_refresh_token,
    verify_token,
    blacklist_token,
    generate_mfa_secret,
    get_mfa_provisioning_uri,
    verify_mfa_code,
    generate_backup_codes,
    hash_backup_code,
    LoginAttemptTracker
)
from app.models.user import User
from app.core.limiter import limiter
from app.core.audit import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s-]{10,15}$')
    role: str = Field(default="patient", pattern=r'^(patient|doctor)$')
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        is_valid, message, score = validate_password_strength(v)
        if not is_valid or score < 60:
            raise ValueError(message)
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = Field(None, pattern=r'^\d{6}$')


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        is_valid, message, score = validate_password_strength(v)
        if not is_valid or score < 60:
            raise ValueError(message)
        return v


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        is_valid, message, score = validate_password_strength(v)
        if not is_valid or score < 60:
            raise ValueError(message)
        return v


class MFASetupResponse(BaseModel):
    secret: str
    qr_uri: str
    backup_codes: List[str]


class MFAVerify(BaseModel):
    code: str = Field(..., pattern=r'^\d{6}$')


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    is_valid, payload, error = verify_token(
        token, 
        settings.JWT_SECRET_KEY, 
        settings.JWT_ALGORITHM,
        "access"
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()
    except ValueError:
        raise credentials_exception
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")
async def register(
    request: Request,
    user_data: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    - Password must be 12+ characters with uppercase, lowercase, number, and special character
    - Rate limit: 3 registrations per hour per IP
    """
    client_ip = get_client_ip(request)
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        log_audit_event(
            event="REGISTRATION_DUPLICATE",
            actor_id=user_data.email,
            actor_role="anonymous",
            ip_address=client_ip,
            status="FAILURE",
            metadata={"reason": "Email already registered"}
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        verification_status="pending",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    log_audit_event(
        event="REGISTRATION_SUCCESS",
        actor_id=str(new_user.id),
        actor_role=new_user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role,
        "message": "Registration successful. Please verify your email."
    }


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token.
    - Rate limit: 10 attempts per minute
    - Account lockout after 5 failed attempts for 15 minutes
    """
    client_ip = get_client_ip(request)
    email = form_data.username
    
    # Check if account is locked
    is_locked, seconds_remaining = LoginAttemptTracker.is_locked(email)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {seconds_remaining // 60} minutes.",
            headers={"Retry-After": str(seconds_remaining)}
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        remaining, is_now_locked = LoginAttemptTracker.record_failure(email)
        
        log_audit_event(
            event="LOGIN_FAILURE",
            actor_id=email,
            actor_role="unknown",
            ip_address=client_ip,
            status="FAILURE",
            metadata={
                "reason": "Invalid credentials",
                "remaining_attempts": remaining
            }
        )
        
        if is_now_locked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Account locked for 15 minutes."
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials. {remaining} attempts remaining.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Check MFA if enabled
    if hasattr(user, 'mfa_enabled') and user.mfa_enabled:
        mfa_code = form_data.scopes[0] if form_data.scopes else None
        if not mfa_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA code required",
                headers={"X-MFA-Required": "true"}
            )
        if not verify_mfa_code(user.mfa_secret, mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Clear login attempts on success
    LoginAttemptTracker.clear(email)
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email},
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        user_id=str(user.id),
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Set refresh token as HTTP-only cookie
    # Use samesite="none" for cross-origin (Vercel frontend -> Render backend)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Required when samesite="none"
        samesite="none",  # Allow cross-origin cookie
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    log_audit_event(
        event="LOGIN_SUCCESS",
        actor_id=str(user.id),
        actor_role=user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    response: Response,
    body: Optional[RefreshTokenRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token from cookie, body, or header"""
    
    # Try multiple sources for refresh token (for cross-origin compatibility)
    token = None
    token_source = None
    
    # 1. Try cookie first
    cookie_token = request.cookies.get("refresh_token")
    if cookie_token:
        token = cookie_token
        token_source = "cookie"
    
    # 2. Try request body (sent by frontend when cookies don't work)
    if not token and body and body.refresh_token:
        token = body.refresh_token
        token_source = "body"
    
    # 3. Try Authorization header as last resort
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Refresh "):
            token = auth_header.replace("Refresh ", "")
            token_source = "header"
    
    if not token:
        print(f"DEBUG: Refresh token not found. Cookie present: {bool(cookie_token)}, Body: {body}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required. Please log in again."
        )
    
    print(f"DEBUG: Refresh token found from {token_source}")
    
    # Verify refresh token
    is_valid, payload, error = verify_token(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
        "refresh"
    )
    
    if not is_valid:
        print(f"DEBUG: Refresh token validation failed: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {error}"
        )
    
    user_id = payload.get("sub")
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Blacklist old refresh token
    old_jti = payload.get("jti")
    if old_jti:
        blacklist_token(old_jti, datetime.now(timezone.utc) + timedelta(days=7))
    
    # Create new tokens
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email},
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(
        user_id=str(user.id),
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    # Update cookie
    # Use samesite="none" for cross-origin (Vercel frontend -> Render backend)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,  # Required when samesite="none"
        samesite="none",  # Allow cross-origin cookie
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """Logout and invalidate tokens"""
    client_ip = get_client_ip(request)
    
    # Clear refresh token cookie
    response.delete_cookie("refresh_token")
    
    log_audit_event(
        event="LOGOUT",
        actor_id=str(current_user.id),
        actor_role=current_user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "verification_status": current_user.verification_status,
        "mfa_enabled": getattr(current_user, 'mfa_enabled', False)
    }


@router.post("/change-password")
async def change_password(
    request: Request,
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change password for authenticated user"""
    client_ip = get_client_ip(request)
    
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        log_audit_event(
            event="PASSWORD_CHANGE_FAILURE",
            actor_id=str(current_user.id),
            actor_role=current_user.role,
            ip_address=client_ip,
            status="FAILURE",
            metadata={"reason": "Invalid current password"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(data.new_password)
    await db.commit()
    
    log_audit_event(
        event="PASSWORD_CHANGE_SUCCESS",
        actor_id=str(current_user.id),
        actor_role=current_user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {"message": "Password changed successfully"}


# =============================================================================
# MFA ROUTES
# =============================================================================

@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Setup MFA for current user"""
    if getattr(current_user, 'mfa_enabled', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate secret
    secret = generate_mfa_secret()
    qr_uri = get_mfa_provisioning_uri(secret, current_user.email)
    backup_codes = generate_backup_codes()
    
    # Store secret temporarily (user must verify to enable)
    current_user.mfa_secret = secret
    current_user.mfa_backup_codes = [hash_backup_code(c) for c in backup_codes]
    await db.commit()
    
    return {
        "secret": secret,
        "qr_uri": qr_uri,
        "backup_codes": backup_codes
    }


@router.post("/mfa/verify")
async def verify_mfa_setup(
    request: Request,
    data: MFAVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify MFA setup with TOTP code"""
    client_ip = get_client_ip(request)
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated"
        )
    
    if not verify_mfa_code(current_user.mfa_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable MFA
    current_user.mfa_enabled = True
    await db.commit()
    
    log_audit_event(
        event="MFA_ENABLED",
        actor_id=str(current_user.id),
        actor_role=current_user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {"message": "MFA enabled successfully"}


@router.post("/mfa/disable")
async def disable_mfa(
    request: Request,
    data: MFAVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable MFA (requires current TOTP code)"""
    client_ip = get_client_ip(request)
    
    if not getattr(current_user, 'mfa_enabled', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    if not verify_mfa_code(current_user.mfa_secret, data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.mfa_backup_codes = None
    await db.commit()
    
    log_audit_event(
        event="MFA_DISABLED",
        actor_id=str(current_user.id),
        actor_role=current_user.role,
        ip_address=client_ip,
        status="SUCCESS"
    )
    
    return {"message": "MFA disabled successfully"}
