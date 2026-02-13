from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Number of threads
    hash_len=32,        # Hash length
    salt_len=16         # Salt length
)

def hash_password(password: str) -> str:
    """Hash password using Argon2id"""
    return ph.hash(password)

def verify_password(password_hash: str, password: str) -> tuple[bool, str | None]:
    """
    Verify password against hash
    Returns: (is_valid, new_hash_if_needed)
    """
    try:
        ph.verify(password_hash, password)
        
        # Check if rehashing is needed (algorithm upgraded)
        if ph.check_needs_rehash(password_hash):
            return True, hash_password(password)  # New hash
        
        return True, None
    except VerifyMismatchError:
        return False, None
