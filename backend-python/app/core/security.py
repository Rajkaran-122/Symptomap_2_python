"""
Security utilities for password hashing and verification
"""

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib
    import secrets


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (or fallback to sha256 for development)"""
    if BCRYPT_AVAILABLE:
        # Production: Use bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    else:
        # Development fallback: Use sha256 with salt
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"sha256${salt}${hashed}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        if BCRYPT_AVAILABLE and not hashed_password.startswith('sha256$'):
            # Production: Use bcrypt verification
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        elif hashed_password.startswith('sha256$'):
            # Development fallback: Verify sha256 hash
            _, salt, stored_hash = hashed_password.split('$')
            computed_hash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
            return computed_hash == stored_hash
        else:
            return False
    except Exception:
        return False

