"""
Production-Grade Security Module for SymptoMap
- Password hashing with Bcrypt (cost factor 12)
- JWT token generation with refresh tokens
- Password strength validation
- MFA/TOTP support
- Token blacklist management
"""

import secrets
import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from jose import JWTError, jwt
import pyotp
import base64

# Bcrypt import with fallback
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

# Configuration
BCRYPT_COST_FACTOR = 12  # 2^12 = 4096 rounds
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
TOKEN_BLACKLIST: Dict[str, datetime] = {}  # In-memory blacklist (use Redis in production)


# =============================================================================
# PASSWORD HASHING
# =============================================================================

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with cost factor 12"""
    if BCRYPT_AVAILABLE:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=BCRYPT_COST_FACTOR)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    else:
        # Fallback for development (NOT production safe)
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"sha256${salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash"""
    try:
        if BCRYPT_AVAILABLE and not hashed_password.startswith('sha256$'):
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        elif hashed_password.startswith('sha256$'):
            _, salt, stored_hash = hashed_password.split('$')
            computed_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
            return secrets.compare_digest(computed_hash, stored_hash)
        return False
    except Exception:
        return False


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

# Common passwords list (abbreviated - use full 10k list in production)
COMMON_PASSWORDS = {
    "password", "123456", "password123", "admin", "letmein", "welcome",
    "monkey", "dragon", "master", "qwerty", "login", "password1",
    "123456789", "12345678", "abc123", "qwerty123", "1q2w3e4r", "admin123"
}


def validate_password_strength(password: str) -> Tuple[bool, str, int]:
    """
    Validate password strength with detailed feedback.
    Returns: (is_valid, message, score 0-100)
    """
    score = 0
    issues = []
    
    # Length check
    if len(password) < PASSWORD_MIN_LENGTH:
        issues.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    elif len(password) >= 16:
        score += 30
    elif len(password) >= 12:
        score += 20
    
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password must be at most {PASSWORD_MAX_LENGTH} characters", 0
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 15
    else:
        issues.append("Add uppercase letters")
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 15
    else:
        issues.append("Add lowercase letters")
    
    # Number check
    if re.search(r'\d', password):
        score += 15
    else:
        issues.append("Add numbers")
    
    # Special character check
    if re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        score += 20
    else:
        issues.append("Add special characters (!@#$%^&*)")
    
    # No common patterns
    if password.lower() not in COMMON_PASSWORDS:
        score += 5
    else:
        issues.append("Password is too common")
        score = min(score, 20)
    
    # No repeated characters (more than 3)
    if not re.search(r'(.)\1{3,}', password):
        score += 5
    else:
        issues.append("Avoid repeated characters")
    
    # Determine strength level
    if score >= 80:
        strength = "Strong"
    elif score >= 60:
        strength = "Good"
    elif score >= 40:
        strength = "Fair"
    else:
        strength = "Weak"
    
    if issues:
        return False, f"{strength}: {', '.join(issues)}", score
    
    return True, f"{strength} password", score


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token with JTI for revocation support"""
    to_encode = data.copy()
    
    # Add token ID for blacklist/revocation
    jti = secrets.token_urlsafe(16)
    to_encode["jti"] = jti
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a refresh token for token rotation"""
    jti = secrets.token_urlsafe(32)
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode = {
        "sub": user_id,
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
    token_type: str = "access"
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Verify a JWT token.
    Returns: (is_valid, payload, error_message)
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        
        # Check token type
        if payload.get("type") != token_type:
            return False, None, "Invalid token type"
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return False, None, "Token has been revoked"
        
        return True, payload, ""
        
    except jwt.ExpiredSignatureError:
        return False, None, "Token has expired"
    except JWTError as e:
        return False, None, f"Invalid token: {str(e)}"


def blacklist_token(jti: str, expires_at: datetime) -> None:
    """Add a token to the blacklist (use Redis in production)"""
    TOKEN_BLACKLIST[jti] = expires_at
    
    # Cleanup expired entries
    now = datetime.now(timezone.utc)
    expired = [k for k, v in TOKEN_BLACKLIST.items() if v < now]
    for k in expired:
        del TOKEN_BLACKLIST[k]


def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted"""
    if jti in TOKEN_BLACKLIST:
        if TOKEN_BLACKLIST[jti] > datetime.now(timezone.utc):
            return True
        else:
            del TOKEN_BLACKLIST[jti]
    return False


# =============================================================================
# MFA / TOTP SUPPORT
# =============================================================================

def generate_mfa_secret() -> str:
    """Generate a new TOTP secret for MFA"""
    return pyotp.random_base32()


def get_mfa_provisioning_uri(secret: str, email: str, issuer: str = "SymptoMap") -> str:
    """Generate provisioning URI for QR code"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify a TOTP code (allows 1 step before/after for clock drift)"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 10) -> list:
    """Generate single-use backup codes for MFA recovery"""
    codes = []
    for _ in range(count):
        # Generate 16-character alphanumeric code
        code = secrets.token_hex(8).upper()
        # Format as XXXX-XXXX-XXXX-XXXX
        formatted = '-'.join([code[i:i+4] for i in range(0, 16, 4)])
        codes.append(formatted)
    return codes


def hash_backup_code(code: str) -> str:
    """Hash a backup code for storage"""
    # Remove dashes and lowercase
    normalized = code.replace('-', '').lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


def verify_backup_code(code: str, hashed_codes: list) -> Tuple[bool, Optional[int]]:
    """Verify a backup code and return its index if valid"""
    code_hash = hash_backup_code(code)
    for i, stored_hash in enumerate(hashed_codes):
        if secrets.compare_digest(code_hash, stored_hash):
            return True, i
    return False, None


# =============================================================================
# RATE LIMITING HELPERS
# =============================================================================

class LoginAttemptTracker:
    """Track failed login attempts per user (use Redis in production)"""
    
    _attempts: Dict[str, list] = {}
    MAX_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    
    @classmethod
    def record_failure(cls, identifier: str) -> Tuple[int, bool]:
        """
        Record a failed login attempt.
        Returns: (remaining_attempts, is_locked)
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=cls.LOCKOUT_MINUTES)
        
        if identifier not in cls._attempts:
            cls._attempts[identifier] = []
        
        # Remove old attempts
        cls._attempts[identifier] = [
            t for t in cls._attempts[identifier] if t > cutoff
        ]
        
        # Add new attempt
        cls._attempts[identifier].append(now)
        
        attempt_count = len(cls._attempts[identifier])
        is_locked = attempt_count >= cls.MAX_ATTEMPTS
        remaining = max(0, cls.MAX_ATTEMPTS - attempt_count)
        
        return remaining, is_locked
    
    @classmethod
    def is_locked(cls, identifier: str) -> Tuple[bool, int]:
        """
        Check if a user is locked out.
        Returns: (is_locked, seconds_remaining)
        """
        if identifier not in cls._attempts:
            return False, 0
        
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=cls.LOCKOUT_MINUTES)
        
        # Count recent attempts
        recent = [t for t in cls._attempts[identifier] if t > cutoff]
        cls._attempts[identifier] = recent
        
        if len(recent) >= cls.MAX_ATTEMPTS:
            # Calculate time until unlock
            oldest = min(recent)
            unlock_time = oldest + timedelta(minutes=cls.LOCKOUT_MINUTES)
            remaining = (unlock_time - now).total_seconds()
            return True, int(max(0, remaining))
        
        return False, 0
    
    @classmethod
    def clear(cls, identifier: str) -> None:
        """Clear attempts after successful login"""
        if identifier in cls._attempts:
            del cls._attempts[identifier]


# =============================================================================
# SECURITY HEADERS
# =============================================================================

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(self), camera=(), microphone=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'"
    )
}


def generate_csrf_token() -> str:
    """Generate a CSRF token"""
    return secrets.token_urlsafe(32)


def generate_session_id() -> str:
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)
