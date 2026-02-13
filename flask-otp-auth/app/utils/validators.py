import re

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """
    Validate password strength
    - At least 8 characters
    - At least one uppercase
    - At least one lowercase
    - At least one number
    - At least one special char
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[ !@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return False
    return True

def validate_phone(phone: str) -> bool:
    """Validate phone number format (basic international)"""
    # Allow + and digits, length 10-15
    pattern = r'^\+?[1-9]\d{9,14}$'
    return bool(re.match(pattern, phone))
